import os
import time
import random


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from config import login, password, href


def logining():
    driver = webdriver.Chrome()

    driver.get(href)

    login_field = driver.find_element(By.NAME, "LoginForm[login]")
    login_field.send_keys(login)

    password_field = driver.find_element(By.NAME, "LoginForm[password]")
    password_field.send_keys(password)

    submit_button = driver.find_element(By.ID, "loginbut")
    submit_button.click()
    time.sleep(0.4)
    return driver
def text_corrector(text):
    while ' ' in text or '\n' in text:
        text = text.replace(' ','`')
        text = text.replace('\n','`')
    while '`' in text:
        text = text.replace('``','`')
        text = text.replace('`',' ')
    return text

if __name__ == '__main__':
    driver = logining()
    driver.get(href)
    counter_new = 0
    counter_old=0

    qa_list = []
    try:
        with open("output.txt", "r", encoding='utf-8') as f:
            lines = f.readlines()
            #print(f'len lines {len(lines)}')
            for i in range(0, len(lines), 5):
                print(f'index {i}')
                question = lines[i].strip().split(": ")[1]
                answer = lines[i+2].strip().split(": ")[1]
                answer_options = eval(lines[i+1].strip().split(": ")[1])
                input_type = lines[i+3].strip().split(": ")[1]
                qa_dict = {'question': question, 'answer': answer, 'answer_options': answer_options, 'input_type': input_type}
                qa_list.append(qa_dict)
            print(f'я записал все в словарь')
    except Exception as e:
        print(f'я не записал все в словарь тк {e}')
        #input()
        qa_list = []
        pass


    #for _ in range(10000):
    while True:
        qa_list=[]
        try:   
            restart_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-success")
            restart_button.click()
            alert = driver.switch_to.alert
            alert.accept()
        except Exception as e:
            pass
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        question_text = html[4923:5300]
        index = question_text.find('<f')
        question_text = question_text[:index]
        question_text = text_corrector(question_text)
        answer_options = driver.find_elements(By.XPATH, "//div[@id='testform-answer']//label")
        answer_list = [option.text.strip() for option in answer_options]


        answer = None
        for qa in qa_list:
            if qa["question"][:50] == question_text[:50]:
                #print(f"""найдено совпадение в радио {qa["question"][:50]} == {question_text[:50]}""")
                #print(qa["answer"],type(qa["answer"]))
                if qa["input_type"] == 'radio':
                    flag = False
                    for i in range(len(answer_options)):
                        for j in range(len(qa["answer_options"])):
                            if answer_options[i].text == qa["answer_options"][j]:
                                answer = i
                                flag= True
                    if not flag:
                        print("Я не нашел ответа в радио")
                elif qa["input_type"] == 'checkbox':
                    flag = False
                    answer = []
                    for i in range(len(answer_options)):
                        for j in range(len(qa["answer_options"])):
                            if answer_options[i].text == qa["answer_options"][j]:
                                answer.append(i)
                                flag = True
                    if not flag:
                        print("Я не нашел ответа в чекбоксе")
                else:
                    print("кнопки не типа радио или чекбокс")

                

        if answer is None:
            #print("я не нашел такого вопроса")
            input_elements = driver.find_elements(By.XPATH, "//div[@id='testform-answer']//input")
            input_type = input_elements[0].get_attribute("type")
            answer_list = sorted(answer_list, key=str.lower)
            if input_type == "radio":
                random_answer = random.choice(answer_options)
                random_answer.click()
                answer_index = answer_options.index(random_answer)
                qa_dict = {'question': question_text, 'answer': answer_index, 'answer_options': answer_list, 'input_type':input_type}
                qa_list.append(qa_dict)
            elif input_type == "checkbox":
                num_answers = random.randint(1, len(answer_options))
                random_answers = random.sample(answer_options, num_answers)
                answer_indices = []
                for answer in random_answers:
                    answer.click()
                    answer_index = answer_options.index(answer) 
                    answer_indices.append(answer_index)
                qa_dict = {'question': question_text, 'answer': answer_indices, 'answer_options': answer_list, 'input_type':input_type}
                qa_list.append(qa_dict)

            with open("output.txt", "a", encoding='utf-8') as f:
                counter_new+=1
                qa_dict['question'] = qa_dict['question'].replace("\n", "")
                f.write(f"Вопрос: {qa_dict['question']}\n")
                f.write(f"Варианты ответа: {qa_dict['answer_options']}\n")
                f.write(f"Ответ: {qa_dict['answer']}\n")
                f.write(f"Тип конопок: {qa_dict['input_type']}\n")
                f.write("\n")
                counter_new+=1
        else:
            #print(type(answer))
            counter_old+=1
            if type(answer) == list:
                for index in answer:
                    answer_options[int(index)-1].click()
            else:
                answer_index = int(answer)
                answer_options[answer_index-1].click()

        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        time.sleep(0.4)
    driver.quit()
    print(f"Записей найдено: {counter_old}, добавлено новых: {counter_new}")
