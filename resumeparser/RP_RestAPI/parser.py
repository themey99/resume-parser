#!/usr/bin/env python3
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
import io
import re

def parse(resume):
    imagewriter = None
    caching = True
    laparams = LAParams()
    retstr = io.StringIO()
    rsrcmgr = PDFResourceManager(caching=caching)
    device = TextConverter(rsrcmgr, retstr, laparams=laparams, imagewriter=imagewriter)
    data = []
    skills = []
    languages = []
    summary = []
    certifications = []
    contact = []
    linkedin = []
    experience = []
    education = []
    complete_experience = []
    complete_education = []
    exp_dict = {}
    edu_dict = {}
    alld = {}

    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(resume, caching=caching, check_extractable=True):
        interpreter.process_page(page)
        data = retstr.getvalue()

    data = re.sub(r'Page \d of \d', 'Page /d of /d', data)
    weird = ["\xa0", "\uf0da", "\x0c", "• ", "* ", "(LinkedIn)", " (LinkedIn)", "\uf0a7", "(Mobile)", "-       ", "●", "Page /d of /d"]
    for i in weird:
        data = data.replace(i, "")

    result_list = data.split('\n')
    lengthOfResultArray = result_list.__len__()

    # Section to validate
    sections = [
        "Contact",
        "Contactar" ,
        "Top Skills",
        "Aptitudes principales",
        "Certifications",
        "Summary",
        "Languages",
        "Education"
    ]

    for i in result_list:
        if i == 'Contact' or i == 'Contactar':
            value = result_list.index(i)
            while True:
                value = value + 1
                contact.append(result_list[value].strip())
                if result_list[value] == '':
                    contact.remove(result_list[value])
                    break

        if i.__contains__('www.linkedin.com'):
            value = result_list.index(i)
            while True:
                linkedin.append(result_list[value])
                value = value + 1
                if result_list[value] == '':
                    break
            if len(linkedin) >= 2:
                ln = []
                merged = linkedin[0] + linkedin[1].strip()
                ln.append(merged)
                linkedin = ln

        if i == 'Top Skills' or i == 'Aptitudes principales':
            value = result_list.index(i)
            while True:
                value = value + 1
                skills.append(result_list[value])
                if result_list[value] == '':
                    skills.remove(result_list[value])
                    break

        if i.__contains__('Certifications') or i.__contains__('Certificationes'):
            value = result_list.index(i)
            while True:
                value = value + 1
                certifications.append(result_list[value])
                if result_list[value] == '':
                    certifications.remove(result_list[value])
                    break

        if i.__contains__('Summary') or i.__contains__('Extracto'):
            value = result_list.index(i)
            while True:
                value = value + 1
                summary.append(result_list[value])
                if result_list[value] == '':
                    summary.remove(result_list[value])
                    break

        if i == 'Languages' or i == 'Idiomas':
            value = result_list.index(i)
            while True:
                value = value + 1
                languages.append(result_list[value])
                if result_list[value] == '':
                    languages.remove(result_list[value])
                    break

        if i == 'Experience' or i == 'Experiencia':
            value = result_list.index(i)
            value = value + 2

            while True:
                # Following condition checks if we have reached the end of the file, this is necessary in case if this section is the last section
                if (value >= lengthOfResultArray - 1):
                    break
                # Following condition checks if we have encountered another section that means this section has finished
                if (str(result_list[value]) in sections):
                    break
                if (result_list[value] == ''):
                    value += 1
                    experience = []
                #Following condition checks if the next three non-empty lines of document are: Name of Company, Position, Period, and Location/Place respectively.
                elif (result_list[value - 1] == "" and result_list[value + 1] != "" and result_list[
                    value + 2].__contains__("-")):
                    #If the above condition is true, we can fetch this experience object and save it in complete_experience array.
                    experience.append(result_list[value]) #Company Name
                    experience.append(result_list[value + 1]) #Job Title
                    experience.append(result_list[value + 2]) #Period
                    experience.append(result_list[value + 3]) #Place
                    listOfExp = ["company", "position", "period", "place"]
                    zipbObj = zip(listOfExp, experience)
                    exp_dict = dict(zipbObj)
                    complete_experience.append(exp_dict)
                    experience = []
                    #As we have fetched 4 indexes in above code, and we know the value at fifth index can either be a description or an empty space,
                    #so we increment the counter to 5.
                    value += 5
                else:
                    value += 1

        if i == 'Education' or i == 'Educación':
            value = result_list.index(i)
            value = value + 1
            index = 0;
            while True:
                #Following condition checks if we have reached the end of the file, this is necessary in case if this section is the last section
                if (value >= lengthOfResultArray - 1):
                    break
                #Following condition checks if we have encountered another section that means this section has finished
                if (str(result_list[value]) in sections):
                        break
                if result_list[value] == '':
                    value = value + 1

                    #Reorder if institution's name has more than two line
                    if (index == 3):
                        education[0] += ' ' + education[1]
                        education[1] = education.pop()

                    if(index > 0):
                        #When we have fetched the 2 values(school & degree) in the education array, we can now create an education object from this array
                        listOfEdu = ["school", "degree"]
                        zipbObj = zip(listOfEdu, education)
                        edu_dict = dict(zipbObj)
                        #Save the education object in complete_education array. This complete_education array will have all the education objects
                        complete_education.append(edu_dict)
                        index = 0
                        education = []
                else:
                    education.append(result_list[value])
                    value = value + 1
                    index += 1

    alld['contact'] = contact
    alld['skills'] = skills
    alld['linkedin'] = linkedin[0]
    alld['skills'] = skills
    alld['certifications'] = certifications
    alld['summary'] = summary
    alld['languages'] = languages
    alld['experience'] = complete_experience
    alld['education'] = complete_education
    device.close()
    retstr.close()

    return alld