from flask import Flask,request,render_template
from flask_cors import CORS,cross_origin
from wikipedia_scrapper import scrapper
from mongodb_operations import mongodb_connection
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


db_name='project'
collection_name='data'



app=Flask(__name__)
#For selenium driver implementation on heroku
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("disable-dev-shm-usage")
CORS(app)
@app.route('/',methods=['GET'])
@cross_origin()
def home_page():
    return render_template('index.html')

@app.route('/main',methods=['POST'])
#@cross_origin()
def main_function():
    if request.method=='POST':
        search_string = request.form['search_string']
        try:

            driver =webdriver.Chrome(ChromeDriverManager().install())
            driver.get("https://en.wikipedia.org/wiki/{}".format(search_string))


            wiki_object=scrapper(search_string,driver)   # creating the object for scrapper class

            summary=wiki_object.make_the_summary()    # this will give the summary of entire article

            refrence_links = wiki_object.links()  # this will give all the reference links

            url_of_images=wiki_object.image_url()   # this will give the  url of all images


            # to convert the images to base64 format
            base64_format_images=wiki_object.store_images_in_folder_and_in_base64_format(urls=url_of_images)


            # creating the object for mongodb_connection class
            mongo_object = mongodb_connection(wiki_object, db_name, collection_name, summary, refrence_links,base64_format_images)

            mongo_object.insert_many_records()
            mongo_object.check_database_is_present()
            mongo_object.check_collection_is_present()


            return render_template('result.html',summary=summary,refrence_links=refrence_links,url_of_images=url_of_images)
        except Exception as e:
            print("error in scrapper class or in mongodb connection class"+str(e))

if __name__=='__main__':
    app.run()
