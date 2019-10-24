# Libraries
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from clustering import cluster_now

# Read database
grammar_questions = pd.read_excel("Grammar Questions.xlsx")
question_data_path = r"Questions data.csv"
student_data_path = r"student_data.csv"

# Flask
app = Flask(__name__)

# Settings
max_question = 5

# Server Memory
question_counter = 0
user_id = ""
number_of_question_correct = 0
prev_question_info = {}
prev_start_time = datetime.now().strftime('%H:%M:%S')
question_difficulty_list = []
question_correct_list = []

# ------------------------- Local functions -------------------------------------------------------------------------
# Extract database question list, return full list of questions with their recorded datas
def question_extraction_full():
    full_dict = {}
    grammar_questions = pd.read_excel("Grammar Questions.xlsx")
    for i in range(0,grammar_questions.shape[0]):
        temporary_dataframe = grammar_questions.iloc[i, :]
        # Keys: Questions, Difficulty, Answer, A, B, C, D, Numeric_difficulty
        temporary_dict = temporary_dataframe.to_dict()
        full_dict[i] = temporary_dict
    #print(full_dict.keys())
    return full_dict
    
# Extract databased on question_counter, previous question correct, time taken, return dictionary with everything    
def question_extraction(counter, correct=0, time_taken=0,num_dif=1):
    next_dif = 1
    # Logic of questions
    if num_dif == 1:
        if correct == 0 or time_taken > 20:
            next_dif = 1
        else:
            next_dif = 2
    elif num_dif == 2:
        if correct == 0:
            next_dif = 1
        elif correct == 1 and time_taken > 20:
            next_dif = 2
        else:
            next_dif = 3
    elif num_dif == 3:
        if correct == 0:
            next_dif = 2
        elif correct == 1 and time_taken > 20:
            next_dif = 3
        else:
            next_dif = 4
    elif num_dif == 4:
        if correct == 0:
            next_dif = 3
        elif correct == 1 and time_taken > 20:
            next_dif = 4
        else:
            next_dif = 5
    else:
        if correct == 0:
            next_dif = 4
        else:
            next_dif = 5
    
    # Filter
    temporary_dataframe = grammar_questions[grammar_questions["Numeric_difficulty"] == next_dif]
    # Random
    temporary_dataframe = temporary_dataframe.sample(5)
    temporary_dataframe = temporary_dataframe.iloc[0,:]
#    temporary_dataframe = temporary_dataframe.iloc[counter, :]
    # Keys: Questions, Difficulty, Answer, A, B, C, D, Numeric_difficulty
    temporary_dict = temporary_dataframe.to_dict()
    return temporary_dict

#Get a list of keys from dictionary which has the given value
def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys

# check if questions are correctly answered
def check_question_correct(prev_dict, answer):
    correct_answer = prev_dict["Answer"]
    correct_option = getKeysByValue(prev_dict, correct_answer)
    print("Correct answer is", correct_option)
    if correct_option[0] == answer:
        print("Answered Correctly")
        return 1
    else:
        print("Answered Wrongly")
        return 0
    
# ------------------------- Flask -------------------------------------------------------------------------
@app.route('/', methods = ['POST', 'GET'])
def register():
   return render_template("register.html")

@app.route('/student_dashboard', methods = ['POST', 'GET'])
def studentdashboard():
    if request.method == 'POST':
      result = request.form
      
      # Acitvate global
      global user_id
      global number_of_question_correct
      global prev_question_info
      global question_counter
      
      # Restart 
      question_counter = 0
      number_of_question_correct = 0
      prev_question_info = {}
      
      user_id = result["Name"]
      
      #Check if it exist in database
      temp_user_df = pd.read_csv(student_data_path)
      temp_user_df = temp_user_df[temp_user_df["ID"] == int(user_id)]
      
      # Create new final result for POST
      final_result = {"Name": user_id, "Scores": []}
      
      # User base exist, extract all past scores and display it
      if temp_user_df.shape[0] != 0:
          for i in range(temp_user_df.shape[0]):
              print(temp_user_df.iloc[i,3])
              final_result["Scores"].append(temp_user_df.iloc[i,3])
              
      print(final_result)
      return render_template("student_dashboard.html",result = final_result, result_len = len(final_result["Scores"]))
  
@app.route('/quiz', methods = ['POST', 'GET'])
def quiz():
    if request.method == 'POST':
      result = request.form
      print(result)
      
      # activate global
      global user_id
      global question_counter
      global prev_question_info
      global number_of_question_correct
      global prev_start_time
      global question_difficulty_list
      global question_correct_list
      
      print("Start time previously is", prev_start_time)
      
      # Check prev question
      try:
          # Append difficulty to list for tracking
          question_difficulty_list.append(prev_question_info["Numeric_difficulty"])
          
          # Question
          question = prev_question_info["Questions"]
          
          # Correct or incorrect
          marks = check_question_correct(prev_question_info, result["option"])
          number_of_question_correct += marks
          
          # Append marks for tracking
          question_correct_list.append(marks)
          
          prev_end_time = datetime.strptime(result['end_time'], '%H:%M:%S')
          prev_start_time = datetime.strptime(prev_start_time, '%H:%M:%S')
          
          # Time taken to complete question
          time_taken_perv_question = (prev_end_time - prev_start_time).total_seconds()
          print("Total time taken :", time_taken_perv_question, "seconds")
          
          # Save the data
          temp_df = pd.read_csv(question_data_path)
          current_shape = temp_df.shape
          temp_df.loc[current_shape[0]+1] = [question, marks, time_taken_perv_question]
          temp_df.to_csv(question_data_path, index = False)
          
      except Exception as e:
          print("No results detected previously. Error", e)
          
      try:
          print("Extracting next question based on previous question's",marks,"and timing",time_taken_perv_question,"and difficulty of", prev_question_info["Numeric_difficulty"])
          final_result = question_extraction(question_counter, marks, time_taken_perv_question,prev_question_info["Numeric_difficulty"])
      except Exception as e:
          final_result = question_extraction(question_counter)
          print("Error in loading question", e)
          
      prev_question_info = final_result
      prev_start_time = datetime.now().strftime('%H:%M:%S')
      
      question_counter += 1
      final_result["question_number"] = question_counter
      
      # If user have not taken the max question 
      if question_counter != max_question + 1:
          final_result["Name"] = user_id
          return render_template("quiz.html",result = final_result)
      else:
          # Save the data
          temp_df = pd.read_csv(student_data_path)
          current_shape = temp_df.shape
          temp_df.loc[current_shape[0]+1] = [user_id, number_of_question_correct, max_question, question_difficulty_list, question_correct_list]
          temp_df.to_csv(student_data_path, index = False)
          

          # Reset data
          alternative_result = {"Name": str(user_id) + " You scored {}/{}".format(number_of_question_correct,max_question), "Scores": []}
          question_counter = 0
          number_of_question_correct = 0
          question_difficulty_list = []
          question_correct_list = []
          prev_question_info = {}
          
          # User base exist, extract all past scores and display it
          temp_user_df = pd.read_csv(student_data_path)
          temp_user_df = temp_user_df[temp_user_df["ID"] == int(user_id)]
          if temp_user_df.shape[0] != 0:
              for i in range(temp_user_df.shape[0]):
                  print(temp_user_df.iloc[i,3])
                  alternative_result["Scores"].append(temp_user_df.iloc[i,3])
          
          return render_template("student_dashboard.html",result = alternative_result, result_len = len(alternative_result["Scores"]))

@app.route('/instructor_dashboard', methods = ['POST', 'GET'])
def instructordashboard():
    # Extract students data
    temp_student_df = pd.read_csv(student_data_path)
    all_students = list(temp_student_df["ID"].unique())
    
    # Length of all students
    student_list_len = len(all_students)
    
    # Obtain all questions difficulty per student
    all_questions_sets = []
    for student in all_students:
        t_df = temp_student_df[temp_student_df["ID"] == student]
        all_questions_sets.append(t_df["past_question"].tolist())
        
    question_numbering = []
    for data in all_questions_sets:
        question_numbering.append(len(data))
        
    return render_template("instructor_dashboard.html", Student = all_students, result_len = student_list_len, question_set = all_questions_sets, question_numbering = question_numbering)

@app.route('/questions', methods = ['POST', 'GET'])
def questions():
    cluster_now()
    final_result = question_extraction_full()
    return render_template("questions.html",result = final_result, result_len= len(final_result.keys()))

if __name__ == '__main__':
   app.run()