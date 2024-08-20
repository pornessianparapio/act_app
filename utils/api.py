import requests

def login_api(email, password):
    url = "https://work-management-ashen.vercel.app/api/userLogin"
    response = requests.post(url, json={"email": email, "password": password})
    if response.status_code == 200:

        data = response.json().get("data")
        if data:
            print(data)
            return {"success": True, "employee_id": data["userId"],"employee_details":data}
        else:
            return {"success": False}
    return {"success": False}



if __name__ == "__main__":
    email = input('Enter email: ')
    password = input('Enter password: ')
    print(login_api(email, password))





