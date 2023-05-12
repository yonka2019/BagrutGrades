import json
import requests
from colorama import Fore, Style

import web
import configparser
import re
from tabulate import tabulate

config = configparser.ConfigParser()


def getAllBagrutData(years=None):
    """
    gets the all bagrut exams according the requested years
    each run the requested data saves, if the new data modified in compare of the previous data, the exam name will be colored as yellow.

    :param years: years list of the requsted exams (could be also not transferred, that would be interpreted as all years)
    :return: table of 'subject | year grade | bagrut grade | final grade' which can be printed
    """
    pattern = r"\s*\(.*\)"
    url = web.BASEURL + "bagrut/grades"
    response = requests.request("GET", url, data=web.payload(), headers=web.getHeader('GET'))
    bagrutGrades = json.loads(response.text)
    data = []

    last_data = extractData()

    for grade in bagrutGrades:
        if ("shnaty" in grade) or ("test" in grade) or ("final" in grade):
            if years is None or str(grade["moed"])[0:4] in years:

                modified_name = f"({grade['semel']})  " + re.sub(pattern, "", grade['name'])

                shnaty = _setGradeColor(str(grade.get('shnaty', "-")))
                test = _setGradeColor(str(grade.get('test', "-")))
                final = _setGradeColor(str(grade.get('final', "-")))

                if _gradeModifed_or_Added(modified_name, shnaty, test, final, last_data):
                    modified_name = Fore.YELLOW + modified_name + Style.RESET_ALL

                data.append([modified_name, shnaty, test, final])

    saveData(data)

    return tabulate(data, headers=["שם", "מגן", "בגרות", "סופי"], tablefmt="pretty")


def _gradeModifed_or_Added(name, shnaty, test, final, prev_data):
    different = True

    for grade in prev_data:
        if re.  sub("\033\[[0-9;]*m", "", grade[0]) == name:  # compare the names without any colors comparing (it could be same name but newly added (colored yellow))
            if grade[1] == shnaty:  # compare the grades without removing the colors this is because if the colors are different - the grade also
                if grade[2] == test:  # ""
                    if grade[3] == final:  # ""
                        different = False  # !! SAME !!
                        break

    return different


def _setGradeColor(grade):
    LOW_GRADE = 65  # 0 - 65 LOW GRADE
    HIGH_GRADE = 90  # 90 - 100 +

    if grade != '-':
        if int(grade) <= LOW_GRADE:
            grade = Fore.RED + grade + Style.RESET_ALL
        elif int(grade) >= HIGH_GRADE:
            grade = Fore.GREEN + grade + Style.RESET_ALL
        else:
            grade = Style.RESET_ALL + grade + Style.RESET_ALL
    else:
        grade = Style.RESET_ALL + grade + Style.RESET_ALL

    return grade


def extractData():
    config.read("config.ini", encoding="utf-8")

    if config.has_section("section1"):
        # Extract the value as a string from the configuration
        value_str = config.get("section1", "last_data")

        # Convert the string back to a list
        return eval(value_str)
    else:
        return ""


def saveData(data):
    config["section1"] = {"last_data": data}

    # Write the configuration to a file
    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)
