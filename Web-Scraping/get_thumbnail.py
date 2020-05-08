from PIL import Image
os.getcwd()
def thumbnail(file, thumbnail, width, height):
    path = os.getcwd()
    thumb = width, height
    img = Image.open(str(path)+ '/' + str(file))
    width, height = img.size

    if width > height:
        delta = width - height
        left = int(delta / 2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta / 2)
        right = width
        lower = width + upper

    img = img.crop((left, upper, right, lower))
    img.thumbnail(thumb, Image.ANTIALIAS)
    img.save(thumbnail)
    img.close()

thumbnail('Rainbow_lorikeet.jpg', 'lorikeet_thumb.jpg', 150, 150)

os.listdir()

Image.open(r'/Users/jean.christophe/Documents/Github/SEO-Projects/Web-Scraping/Rainbow_lorikeet.jpg')