import os
import time
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from config import login, password, href

driver = webdriver.Chrome()

driver.get(href)

login_field = driver.find_element(By.NAME, "LoginForm[login]")
login_field.send_keys(login)

password_field = driver.find_element(By.NAME, "LoginForm[password]")
password_field.send_keys(password)

submit_button = driver.find_element(By.ID, "loginbut")
submit_button.click()
time.sleep(0.4)
driver.get(href)

counter_new = 0
counter_old = 0
qa_list = []

class Task():
    def __init__(self,question,answers):
        self.question = question
        self.answers = answers
        


for _ in range(1):
    try:
        with open("output.txt", "r") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 4):
                #print(i)
                if i+3 >= len(lines):
                    break
                question = lines[i].strip().split(": ")[1]
                answer = lines[i+2].strip().split(": ")[1]
                answer_options = eval(lines[i+1].strip().split(": ")[1])
                qa_dict = {'question': question, 'answer': answer, 'answer_options': answer_options}
                qa_list.append(qa_dict)


    except FileNotFoundError:
        pass
    try:   
        restart_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-success")
        restart_button.click()

        alert = driver.switch_to.alert
        alert.accept()
    except Exception as e:
        pass
    for i in range(58):
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try:
            question_text = html[4927:5300]
            index = question_text.find('<f')
            question_text = question_text[:index]
            if question_text[0] == ' ':
                question_text = question_text[1:]
            answer_options = driver.find_elements(By.XPATH, "//div[@id='testform-answer']//label")
            answer_list = [option.text.strip() for option in answer_options]
            

            answer = None
            for qa in qa_list:
                temp1 = qa["question"][:]
                temp1 = temp1.replace("\n", "")
                temp1 = temp1.replace(" ", "")
                temp = question_text[:]
                temp = temp.replace("\n", "")
                temp = temp.replace(" ", "")
                #print(qa["question"],temp,qa["question"] == temp)
                
                if temp1 == temp:
                    counter_old+=1
                    #print(qa["answer"],type(qa["answer"]))
                    answer = qa["answer"]
                    if type(answer) == str:
                        if len(answer)>2:
                            answer = [int(i) for i in answer[1::3]]
                        else:
                            answer = int(answer)
                    

            if answer is None:
                input_elements = driver.find_elements(By.XPATH, "//div[@id='testform-answer']//input")
                input_type = input_elements[0].get_attribute("type")
                if input_type == "radio":
                    random_answer = random.choice(answer_options)
                    random_answer.click()
                    answer_index = answer_options.index(random_answer) 
                    qa_dict = {'question': question_text, 'answer': answer_index, 'answer_options': answer_list}
                    qa_list.append(qa_dict)
                elif input_type == "checkbox":
                    num_answers = random.randint(1, len(answer_options))
                    random_answers = random.sample(answer_options, num_answers)
                    answer_indices = []
                    for answer in random_answers:
                        answer.click()
                        answer_index = answer_options.index(answer) 
                        answer_indices.append(answer_index)
                    qa_dict = {'question': question_text, 'answer': answer_indices, 'answer_options': answer_list}
                    qa_list.append(qa_dict)

                with open("output.txt", "a") as f:
                    counter_new+=1
                    qa_dict['question'] = qa_dict['question'].replace("\n", "")
                    f.write(f"Вопрос: {qa_dict['question']}\n")
                    f.write(f"Варианты ответа: {qa_dict['answer_options']}\n")
                    f.write(f"Ответ: {qa_dict['answer']}\n")
                    f.write("\n")
            else:
                #print(type(answer))
                if type(answer) == list:
                    for index in answer:
                        answer_options[int(index)-1].click()
                else:
                    answer_index = int(answer)
                    answer_options[answer_index-1].click()

        except Exception as e:
            print(f'Error in range(18):',e)

        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        time.sleep(0.4)
driver.quit()
print(f'Записей добавлено: {counter_new}\nЗаписей найдено: {counter_old}')
