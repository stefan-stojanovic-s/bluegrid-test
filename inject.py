from bs4 import BeautifulSoup
import json
import sys

def inject_li_tag(message):
    #getting the index file
    with open("index.html") as f:
        soup = BeautifulSoup(f.read(),"lxml")

    new_li_tag = soup.new_tag("li")
    new_li_tag.string = message

    #injecting the tag
    soup.html.body.ul.append(new_li_tag)

    with open("index.html","w", encoding = "utf-8") as f:
        f.writelines(str(soup))

if __name__ == "__main__" :
    try:
        if len(sys.argv) > 1:
            message = sys.argv[1]
            inject_li_tag(message)
            print(json.dumps({
                "subject" : "REPORT - Message injected SUCCESS",
                "message" : message,
            }))
    except:
        print(json.dumps({
                "subject" : "REPORT - Message injected FAILED",
                "message" : None,
            }))