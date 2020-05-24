import json
import urllib.parse
import requests

print('Knowledge Graph API')
api_key = open('api-key.txt').read()
while True:
    query = input('Enter query: ')
    querynum = input('How many results do you want? (Number): ')
    queryDesc = input('Return Knowledge Graph description? (Y/N): ')
    typequestion = input('Add entity filter? (Y/N): ')
    if typequestion == 'Y':
        print('Check Schema.org for list of entity "types": https://schema.org/docs/schemas.html')
        kptype = input('What type of entity do you want? ')

    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': str(query),
        'limit': int(querynum),
        'indent': True,
        'key': api_key,
}

    if typequestion == 'Y':
        params['types'] = kptype

    url = f'{service_url}?{urllib.parse.urlencode(params)}'
    print(url)
    response = requests.get(url, verify=False)
    json_response = json.loads(response.text)

    print(f'Query: {query}' + '\n')

    try:
        for element in json_response['itemListElement']:
            if queryDesc == 'Y':
                print(element['result']['name'] + ' (ID: ' + element['result']['@id'] + ')' + ' \
                (Score: ' + str(element['resultScore']) + ')' + 'Description: ' + element['result']['description'])
            else:
                print(element['result']['name'] + ' (ID: ' + element['result']['@id'] + ')' + ' \
                (Score: ' + str(element['resultScore']) + ')')
    except KeyError:
        print('<Error: Name not found>')

    print('')
    savefiles = input('Save files locally?(Y/N) ')
    if savefiles == 'Y':
        download_dir = 'knowledge-graph-results.csv'
        file = open(download_dir, 'w')
        columnTitleRow = "Query, Name, MID, Score, Description\n"
        file.write(columnTitleRow)
            
        try:
            for element in json_response['itemListElement']:
                if queryDesc == 'Y':
                    q = query
                    name = element['result']['name']
                    ID = element['result']['@id']
                    score = element['resultScore']
                    description = element['result']['description']
                    descrip2 = f'"{description}"'

                    row = f'{q},{name},{ID},{score},{descrip2}\n'
                    file.write(row)
                else:
                    q = query
                    name = element['result']['name']
                    ID = element['result']['@id']
                    score = element['resultScore']
                    description = element['result']['description']
                    row2 = f'{q},{name},{ID},{score}\n'
                    file.write(row2)
        except KeyError:
            print('')
    if savefiles == 'Y':
        print(f'Success. Results saved locally at {download_dir}.')
        file.close()
    choice = input('Continue Querying?(Y/N): ')
    if choice == 'N':
        break

