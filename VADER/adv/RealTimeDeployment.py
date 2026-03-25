from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    review = data['review']
    processed_review = preprocess_text(review)
    X = vectorizer.transform([processed_review])
    prediction = model.predict(X)
    sentiment = 'positive' if prediction == 1 else ('negative' if prediction == 0 else 'neutral')
    return jsonify({
   'sentiment': sentiment})

if __name__ == '__main__':
    app.run(debug=True)
