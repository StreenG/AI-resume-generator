from flask import Flask, render_template, redirect, request, url_for, Response
from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, TextAreaField, StringField
from wtforms.validators import Length
import openai
import translators as ts
import pdfkit
import os
from dotenv import load_dotenv

path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
wkhtmltopdf_config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)



app = Flask(__name__)
app.config['SECRET_KEY'] = "HTHAERGDSAA1234"



def configure():
    load_dotenv()

#build the form.
class MyForm(FlaskForm):
    name = StringField("שם")
    l_name = StringField("שם משפחה")
    work_place = StringField("מקום עבודה")
    job_role = StringField("תפקיד")
    work_exp = TextAreaField("ספר על עצמך")
    generate_ai_btn = SubmitField("צור עם בינה מלאכותית")
    work_exp_from_year = StringField("מ", validators=[Length(max=4, min=4)])
    work_exp_to_year = StringField("עד", validators=[Length(max=4, min=4)])
    work_achievements = TextAreaField("ניסיון תעסוקתי והישגים")
    generate_achievements_btn = SubmitField("צור עם בינה מלאכותית")
    education = TextAreaField("השכלה")
    edu_degree = StringField("תואר")
    education2 = TextAreaField("השכלה (לא חובה)")
    edu_from_year = StringField("מ", validators=[Length(max=4, min=4)])
    edu_to_year = StringField("עד", validators=[Length(max=4, min=4)])
    edu_from_year2 = StringField("מ", validators=[Length(max=4, min=4)])
    edu_to_year2 = StringField("עד", validators=[Length(max=4, min=4)])
    edu_degree2 = StringField("תואר (לא חובה)")
    address = StringField("כתובת/מיקוד")
    phone = StringField("טלפון")
    email = EmailField("אימייל")
    submit_btn = SubmitField("ליצור קורות חיים")
    generate_ai_skills_btn = SubmitField("צור עם בינה מלאכותית")
    skills = TextAreaField("כישורים (להפריד עם פסיק בין כל אחד)")
    linkedin = StringField("LinkedIn")
    github = StringField("GitHub")



#home function. gets the data from the forms, and sends prompts to specified fields in order to return a value which is translated and then passed to other functions.
@app.route("/", methods=["GET","POST"])
def home():
    form = MyForm()
    if form.is_submitted():
        name = form.name.data
        l_name = form.l_name.data

        work_place = form.work_place.data
        work_exp = form.work_exp.data
        job_role = form.job_role.data

        work_exp_from_year = form.work_exp_from_year.data
        work_exp_to_year = form.work_exp_to_year.data
        work_achievements = form.work_achievements.data.split(',')
        generate_achievements_btn = form.generate_achievements_btn

        education = form.education.data
        edu_degree = form.edu_degree.data
        edu_from_year = form.edu_from_year
        edu_to_year = form.edu_to_year
        education2 = form.education2.data
        edu_from_year2 = form.edu_from_year2
        edu_to_year2 = form.edu_to_year2

        address = form.address.data
        phone = form.phone.data
        email = form.email.data

        linkedin = form.linkedin.data
        github = form.github.data

        skills = form.skills.data.split(',')

        #start AI conversation with a prompt
        if form.generate_ai_btn.data:
            ai_response = open_ai_start_conversation(f"Generate a summary that emphasizes my unique selling points and "
                                                     f"sets me apart from other candidates for this job but write it as "
                                                     f"you were me in 4 sentences, and use important"
                                                     f"keywords.{ts.translate_text(form.work_exp.data)}")
            translated_to_hebrew = ts.translate_text(ai_response, to_language="he")
            return redirect(url_for("edit_template", ai_response=translated_to_hebrew, **form.data))
        # start AI conversation with a prompt
        if form.generate_ai_skills_btn.data:
            ai_skills_response = open_ai_start_conversation(
                f"Write all the skills associated with this short description."
                f" seperate the skills with a comma like this - a, b, c, d. write 8 of the most important skills."
                f"{ts.translate_text(form.work_exp.data)}")
            skills_translated_to_hebrew = ts.translate_text(ai_skills_response, to_language="he")
            return redirect(url_for("edit_template", ai_skills_response=skills_translated_to_hebrew, **form.data))
        # start AI conversation with a prompt
        if form.generate_achievements_btn.data:
            ai_achievements_response = open_ai_start_conversation(
                f"Write all the significant skills and Key Accomplishments and mix between them, for this role:{ts.translate_text(form.job_role.data)}"
                f" that i did and talk as if you were me, limit to three sentences")
            ai_achievements_translated_to_hebrew = ts.translate_text(ai_achievements_response, to_language="he")
            return redirect(url_for("edit_template", ai_achievements_response=ai_achievements_translated_to_hebrew, **form.data))
        else:
            return redirect(url_for("template", **form.data))
    return render_template("home.html", form=form)
#this is a function which generates the function. it gets the data from the forms and then implements in the html.
@app.route("/CV", methods=["GET", "POST"])
def template():
    #Get form data from the redirect **form.data
    name = request.args.get('name')
    l_name = request.args.get('l_name')

    work_place = request.args.get('work_place')
    work_exp = request.args.get('work_exp')

    job_role = request.args.get('job_role')
    ai_response = request.args.get('ai_response')

    work_exp_from_year = request.args.get('work_exp_from_year')
    work_exp_to_year = request.args.get('work_exp_to_year')
    work_achievements = request.args.get('work_achievements')
    education = request.args.get('education')
    edu_degree = request.args.get('edu_degree')

    education2 = request.args.get('education2')
    edu_from_year = request.args.get('edu_from_year')
    edu_to_year = request.args.get('edu_to_year')
    edu_from_year2 = request.args.get('edu_from_year2')
    edu_to_year2 = request.args.get('edu_to_year2')
    edu_degree2 = request.args.get('edu_degree2')

    address = request.args.get('address')
    phone = request.args.get('phone')
    email = request.args.get('email')

    linkedin = request.args.get('linkedin')
    github = request.args.get('github')

    skills = request.args.get('skills')
    ai_skills_response = request.args.get('ai_skills_response')
    ai_achievements_response = request.args.get('ai_achievements_response')

    #lists to split for splitting sentences for lists
    work_achievements_list = work_achievements.split('.') if work_achievements else []
    ai_achievements_list = ai_achievements_response.strip().split('.') if ai_achievements_response else []
    ai_skills_list = ai_skills_response.split(',') if ai_skills_response else []
    skills_list = skills.split(',') if skills else []
    #pass all the data to the template
    return render_template("CV.html", name=name, l_name=l_name,work_place=work_place, work_exp=work_exp,
                           job_role=job_role, work_exp_from_year=work_exp_from_year, work_exp_to_year=work_exp_to_year,
                           education=education, edu_degree=edu_degree, address=address, phone=phone, email=email, skills=skills_list,
                           work_achievements=work_achievements_list, edu_from_year=edu_from_year, edu_to_year=edu_to_year ,
                           education2=education2, edu_to_year2=edu_to_year2, edu_from_year2=edu_from_year2,
                           edu_degree2=edu_degree2, ai_response=ai_response, ai_skills_response=ai_skills_response,
                           ai_achievements_response=ai_achievements_response, linkedin=linkedin, github=github)

#This is a function for editing the template, using request.args.get to get the data from the forms and then passing it to a new route /edit with the same values.
@app.route("/edit", methods=["GET", "POST"])
def edit_template():
    edit_form = MyForm()
    name = request.args.get('name')
    l_name = request.args.get('l_name')
    work_place = request.args.get('work_place')
    ai_response = request.args.get('ai_response')
    work_exp = request.args.get('work_exp')
    job_role = request.args.get('job_role')

    work_exp_from_year = request.args.get('work_exp_from_year')
    work_exp_to_year = request.args.get('work_exp_to_year')
    work_achievements = request.args.get('work_achievements')

    education = request.args.get('education')
    edu_degree = request.args.get('edu_degree')
    education2 = request.args.get('education2')
    edu_from_year = request.args.get('edu_from_year')
    edu_to_year = request.args.get('edu_to_year')
    edu_from_year2 = request.args.get('edu_from_year2')
    edu_to_year2 = request.args.get('edu_to_year2')
    edu_degree2 = request.args.get('edu_degree2')

    address = request.args.get('address')
    phone = request.args.get('phone')
    email = request.args.get('email')

    linkedin = request.args.get('linkedin')
    github = request.args.get('github')

    skills = request.args.get('skills')
    ai_achievements_response = request.args.get('ai_achievements_response')
    ai_skills_response = request.args.get('ai_skills_response')

    # Pre-fill the form fields with existing data
    edit_form.name.data = name
    edit_form.l_name.data = l_name
    edit_form.work_place.data = work_place
    edit_form.job_role.data = job_role

    #if theres already an AI, prefill the spot with the ai instead of the user data
    if ai_response:
        edit_form.work_exp.data = ai_response
    else:
        edit_form.work_exp.data = work_exp
    edit_form.work_exp_from_year.data = work_exp_from_year
    edit_form.work_exp_to_year.data = work_exp_to_year
    # if theres already an AI, prefill the spot with the ai instead of the user data
    if ai_achievements_response:
        edit_form.work_achievements.data = ai_achievements_response
    else:
        edit_form.work_achievements.data = work_achievements
    edit_form.education.data = education
    edit_form.edu_degree.data = edu_degree
    edit_form.education2.data = education2
    edit_form.edu_from_year.data = edu_from_year
    edit_form.edu_to_year.data = edu_to_year
    edit_form.edu_from_year2.data = edu_from_year2
    edit_form.edu_to_year2.data = edu_to_year2
    edit_form.edu_degree2.data = edu_degree2
    edit_form.address.data = address
    edit_form.phone.data = phone
    edit_form.email.data = email
    edit_form.linkedin.data = linkedin
    edit_form.github.data = github
    # if theres already an AI, prefill the spot with the ai instead of the user data
    if ai_skills_response:
        edit_form.skills.data = ai_skills_response
    else:
        edit_form.skills.data = skills

    if edit_form.is_submitted():
        return render_template("template.html", ai_response=ai_response,
                               ai_skills_response=ai_skills_response, ai_achievements_response=ai_achievements_response)
    return render_template("home.html", form=edit_form)


#this is the function for the ChatGPT library which sends a prompt with a message and user_data
def open_ai_start_conversation(user_data):
    messages = [
        {"role": "system", "content": "You are an experienced resume writer"},
        {"role": "user", "content": user_data}
    ]
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        max_tokens=400,
        api_key=os.getenv('OPEN_AI_API_KEY')
    )
    return response.choices[0].message['content'].strip()

@app.route('/convert-to-pdf', methods=["GET", "POST"])
def convert_to_pdf():
    #get the data from the form so you can insert to the pdf.
    data = {
        'name': request.args.get('name'),
        'l_name': request.args.get('l_name'),
        'address': request.args.get('address'),
        'phone': request.args.get('phone'),
        'email': request.args.get('email'),
        'work_exp': request.args.get('work_exp'),
        'job_role': request.args.get('job_role'),
        'work_exp_from_year': request.args.get('work_exp_from_year'),
        'work_exp_to_year': request.args.get('work_exp_to_year'),
        'work_achievements': request.args.get('work_achievements'),
        'education': request.args.get('education'),
        'edu_degree': request.args.get('edu_degree'),
        'education2': request.args.get('education2'),
        'edu_from_year': request.args.get('edu_from_year'),
        'edu_to_year': request.args.get('edu_to_year'),
        'edu_from_year2': request.args.get('edu_from_year2'),
        'edu_to_year2': request.args.get('edu_to_year2'),
        'edu_degree2': request.args.get('edu_degree2'),
        'linkedin': request.args.get('linkedin'),
        'github': request.args.get('github'),
        'skills': request.args.get('skills'),
        'ai_achievements_response': request.args.get('ai_achievements_response'),
        'ai_skills_response':  request.args.get('ai_skills_response'),
    }
    #split the data again in order for it to be displayed correctly.
    skills_list = data['skills'].split(',') if data['skills'] else []
    work_achievements_list = data['work_achievements'].split('.') if data['work_achievements'] else []

    #if statement so whenever you convert to pdf, the buttons will be invisible in the CV.HTML
    pdf_conversion_in_progress = True
    if pdf_conversion_in_progress:
        data['pdf_conversion_in_progress'] = True

    keys_to_exclude = ['skills', 'work_achievements']

    # Convert boolean values to strings in the combined data in order to convert to pdf.
    combined_data = {key: str(value) for key, value in data.items() if key not in keys_to_exclude}


    # Render the template to a temporary HTML file, pass the lists for correct formatting.
    rendered_template = render_template("CV.html", skills=skills_list, work_achievements=work_achievements_list,
                                        **combined_data)
    temp_html_file = "temp_cv.html"

    with open(temp_html_file, "w", encoding="utf-8") as f:
        f.write(rendered_template)

    # Convert the temporary HTML file to PDF
    pdf_file = "resume.pdf"
    pdfkit.from_file(temp_html_file, pdf_file, configuration=wkhtmltopdf_config,
                     options={"enable-local-file-access": ""})

    # Remove the temporary HTML file
    os.remove(temp_html_file)

    headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename="{pdf_file}"'
    }
    with open(pdf_file, "rb") as f:
        pdf_data = f.read()

    response = Response(pdf_data, headers=headers)
    return response




#runs the program normally and enables debug mode
if __name__ == "__main__":
    configure()
    app.run(debug=True)