import pickle
import requests
#importing the inputScript file used to analyze the URL import inputScript
import inputScript
import numpy as np
import sklearn

from flask import Flask, jsonify, render_template, request

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "tPYoi6dc_hrBJSa8H15zbwIZeBWGOqS5bb9MEvefIDiM"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


#load model 
app = Flask(__name__) 
model = pickle.load(open('Phishing_website.pkl', 'rb'))


#Redirects to the page to give the user iput URL.
@app.route('/')
def predict(): 
    return render_template('index.html') 


#Fetches the URL given by the URL and passes to inputScript
@app.route('/y_predict', methods=['POST'])
def y_predict():

    '''
    For rendering results on HTML GUI
    '''

    url = request.form['URL']
    checkprediction = inputScript.main(url)
    prediction = model.predict(checkprediction)
    print(prediction)
    output=prediction [0]
    if(output==1):
        pred="Your are safe!! This is a Legitimate Website."

    else:
        pred="You are on the wrong site. Be cautious!" 
    
    return render_template('index.html', prediction_text='{}'.format(pred), url=url)


# NOTE: manually define and pass the array(s) of values to be scored in the next line
payload_scoring = {"input_data": [{"fields": "url", "values": "prediction"}]}

response_scoring = request.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/948c1580-ae46-442d-9336-527744e09a09/predictions?version=2022-11-05', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
print("Scoring response")
print(response_scoring.json())


#Takes the input parameters fetched from the URL by inputScript and returns the predictions 
@app.route('/predict_api', methods=['POST'])
  
def predict_api():

    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.y_predict ( [np.array(list(data.values()))])

    output = prediction[0]
    return jsonify (output)

if __name__ == '__main__' :
    app.run(host='0.0.0.0', debug=True)
