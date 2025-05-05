import requests

def test_farmers_alert(city):
    url = "http://127.0.0.1:5001/farmers"
    data = {'city': city}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(f"Test for city '{city}' succeeded. Response content:")
        print(response.text)
    else:
        print(f"Test for city '{city}' failed with status code: {response.status_code}")

if __name__ == "__main__":
    test_city = "Tanakpur"  # Change to any city to test
    test_farmers_alert(test_city)
