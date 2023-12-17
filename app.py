from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import plotly.express

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs = {'class':'history-rates-data'})
row = table.find_all('a', attrs = {'class':'w'})

row_length = len(row)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here
    Date = table.find_all('a', attrs = {'class':'w'})[i].text

    Harga = table.find_all('span', attrs = {'class':'w'})[i].text
    Harga = Harga.strip()
    temp.append((Date,Harga)) 

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('Date','Harga'))

#insert data wrangling here
df['Harga']= df['Harga'].apply(lambda x: x.replace('$1 = Rp','')).str.replace(',','')
df['Date'] = pd.to_datetime(df['Date'])
df['Harga'] = df['Harga'].astype('float64')
df.set_index('Date',inplace=True)
#end of data wranggling 

# for boxplot
df1 = df.copy()
df1 = df1.reset_index()
df1['Quarter']= df1['Date'].dt.to_period('Q')


@app.route("/")
def index():
 
   card_data = f'{df["Harga"].mean().round(2)}' #be careful with the " and '

   # generate plot
   fig, ax = plt.subplots(figsize=(11, 6))
   df.plot(ax=ax)
 
    # Rendering plot for df
   figfile = BytesIO()
   plt.savefig(figfile, format='png', transparent=True)
   figfile.seek(0)
   figdata_png = base64.b64encode(figfile.getvalue())
   plot_result = str(figdata_png)[2:-1]
   
   fig2, ax2 = plt.subplots(figsize=(11, 6))
   df1.boxplot(column='Harga', by='Quarter', ax=ax2)
   
    # Rendering plot for df1
   figfile2 = BytesIO()
   plt.savefig(figfile2, format='png', transparent=True)
   figfile2.seek(0)
   figdata_png2 = base64.b64encode(figfile2.getvalue())
   plot_result2 = str(figdata_png2)[2:-1]




   # render to html
   return render_template('index.html',
       card_data = card_data,
       plot_result=plot_result,
       plot_result2=plot_result2)




if __name__ == "__main__":
   app.run(debug=True)