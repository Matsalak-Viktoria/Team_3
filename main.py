import cherrypy
import csv
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

clu_endpoint = "https://psymonitor.cognitiveservices.azure.com/"
clu_key = "fb821673335b408f9b324740f5c3291a"
project_name = "PsyMonitor"
deployment_name = "PsyMonitor"
file_name = "../Items.csv"

with open(file_name, "r") as file:
    questions = list(csv.reader(file))

count = 0

# Total sum of scores
sum_s_t = 0

# Sum of scores for Factor 1
sum_s_1 = 0

# Sum of scores for Factor 2
sum_s_2 = 0

# Sum of scores for Factor 3
sum_s_3 = 0

# Sum of scores for Factor 4
sum_s_4 = 0

# Sum of scores for Factor 5
sum_s_5 = 0

def personalityFeedbackAnalyse(query):
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    with client:
        return client.analyze_conversation(
            task={
                "kind": "Conversation",
                "analysisInput": {
                    "conversationItem": {
                        "participantId": "1",
                        "id": "1",
                        "modality": "text",
                        "language": "it",
                        "text": query
                    },
                    "isLoggingEnabled": False
                },
                "parameters": {
                    "projectName": project_name,
                    "deploymentName": deployment_name,
                    "verbose": True
                }
            }
        )

i = 0
class Questionnaire(object):

    @cherrypy.expose
    def index(self):
        global i
        if i < 50:
            out = questions[i][0]
        else:
            out = ""
        return out, """<html>
              <head></head>
              <body>
                <form method="post" action="send">
                    <p>Enter your answer:</p>
                    <label><input type="text" value="" name="answer"></label>
                    <button type="submit">Send</button>
                </form>
              </body>
            </html>"""

    @cherrypy.expose
    def send(self, answer):
        global count, sum_s_t, sum_s_1, sum_s_2, sum_s_3, sum_s_4, sum_s_5, i
        result = personalityFeedbackAnalyse(answer)
        if (i % 2 == 0 and i != 28 and i != 38 and i != 48) or i == 39 or i == 41 or i == 47 or i == 49:
            if result["result"]["prediction"]["topIntent"] == "StrongDisagree":
                answer = 1
            elif result["result"]["prediction"]["topIntent"] == "Disagree":
                answer = 2
            elif result["result"]["prediction"]["topIntent"] == "NeitherAgree":
                answer = 3
            elif result["result"]["prediction"]["topIntent"] == "Agree":
                answer = 4
            else:
                answer = 5
        else:
            if result["result"]["prediction"]["topIntent"] == "StrongDisagree":
                answer = 5
            elif result["result"]["prediction"]["topIntent"] == "Disagree":
                answer = 4
            elif result["result"]["prediction"]["topIntent"] == "NeitherAgree":
                answer = 3
            elif result["result"]["prediction"]["topIntent"] == "Agree":
                answer = 2
            else:
                answer = 1

        if count == 0:
            sum_s_1 += answer
            count += 1
        elif count == 1:
            sum_s_2 += answer
            count += 1
        elif count == 2:
            sum_s_3 += answer
            count += 1
        elif count == 3:
            sum_s_4 += answer
            count += 1
        else:
            sum_s_5 += answer
            count = 0

        sum_s_t += answer

        if i < 50:
            i += 1

        val_1 = sum_s_1 / sum_s_t
        val_2 = sum_s_2 / sum_s_t
        val_3 = sum_s_3 / sum_s_t
        val_4 = sum_s_4 / sum_s_t
        val_5 = sum_s_5 / sum_s_t

        print("Sum of scores for Factor 1:", sum_s_1)
        print("Sum of scores for Factor 2:", sum_s_2)
        print("Sum of scores for Factor 3:", sum_s_3)
        print("Sum of scores for Factor 4:", sum_s_4)
        print("Sum of scores for Factor 5:", sum_s_5)
        print("Total sum of scores:", sum_s_t)
        print("Value 1: {0:.2f}".format(val_1))
        print("Value 2: {0:.2f}".format(val_2))
        print("Value 3: {0:.2f}".format(val_3))
        print("Value 4: {0:.2f}".format(val_4))
        print("Value 5: {0:.2f}".format(val_5))
        raise cherrypy.HTTPRedirect("index")

cherrypy.quickstart(Questionnaire())
