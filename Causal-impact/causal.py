from causalimpact import CausalImpact
from functools import reduce
import numpy as np
import pandas as pd 
import searchconsole


class Causal:


    def __init__(self, account, intervention, test_sites, control_sites='', months=-16, metric='clicks', dimension='date'):
        self.account = account
        self.test_sites = test_sites
        self.control_sites = control_sites if control_sites else None
        self.intervention = intervention
        self.metric = metric
        self.months = months
        self.dimension = dimension


    def run_causal(self):
        """Combines all the functions together

        Returns:
            [df]: dataframe on which CI was run
        """        
        data = self.create_master_df()
        pre_period, post_period = self.get_pre_post(data)
        self.make_report(data, pre_period, post_period)
        return data


    def extract_from_list(self, sites):
        """Extract GSC data from a list of sites

        Args:
            sites (list): list of properties validated in GSC

        Returns:
            [list]: List of dataframes extracted from GSC
        """        
        print(f'Extracting data for {sites}')
        dfs = []
        for site in sites:
            print(f'Extracting: {site}')
            webproperty = self.account[site]
            report = webproperty.query\
                    .range('today', months=self.months)\
                    .dimension(self.dimension)\
                    .get()
            df = report.to_dataframe()
            dfs.append(df)
        return dfs


    def concat_test(self, dfs):
        """Concatenate the dataframes used for testing

        Args:
            dfs (list): List of dataframes extracted from GSC

        Returns:
            dataframe: merged test dataframes summed together 
        """        
        concat_df = pd.concat(dfs)
        test = concat_df.groupby('date')[['clicks', 'impressions']].sum()
        test = test.reset_index()
        test['ctr'] = test['clicks'] / test['impressions']
        return test


    def concat_control(self, dfs):
        """Concatenate the dataframes used for control

        Args:
            dfs (list): List of dataframes extracted from GSC

        Returns:
            dataframe: merged control dataframes. 1 metric column by df 
        """        
        control_data = []
        for i in range(len(dfs)):
            df = dfs[i][['date', self.metric]]
            df = df.rename(columns={self.metric: f'X{i}'})
            control_data.append(df)
        control = reduce(
                lambda left, right: pd.merge(
                        left, right, on=['date'],
                        how='outer'),
                control_data
                )
        return control


    def create_master_df(self):
        """Create a master df for a given metric with:
        y = test (target)
        Xn = control (features)

        Returns:
            dataframe: df with target and features based on list of sites
        """        
        test = self.extract_from_list(self.test_sites)
        test = self.concat_test(test)
        y = test[['date', self.metric]].rename(columns={self.metric:'y'})

        if self.control_sites:
            control = self.extract_from_list(self.control_sites)
            X = self.concat_control(control)
            data = y.merge(X, on='date', how='left')
        else:
            data = y
        return data.sort_values(by='date').reset_index(drop=True)


    def get_pre_post(self, data):
        """Get pre-post periods based on the intervention date

        Args:
            data (dataframe): df comming from create_master_df()

        Returns:
            tuple: tuple of lists showing index edges of period before and after intervention
        """        
        pre_start = min(data.index)
        pre_end = int(data[data['date'] == self.intervention].index.values)
        post_start = pre_end + 1
        post_end = max(data.index)

        pre_period = [pre_start, pre_end] 
        post_period = [post_start, post_end]
        return pre_period, post_period


    def make_report(self, data, pre_period, post_period):
        """Creates the built-in CausalImpact report

        Args:
            data (dataframe): df comming from create_master_df()
            pre_period (list): list coming from get_pre_post()
            post_period (list): list coming from get_pre_post()
        """        
        ci = CausalImpact(data.drop(['date'], axis=1), pre_period, post_period)
        print(ci.summary())
        print(ci.summary(output='report'))
        ci.plot()
