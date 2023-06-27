import json
import requests
import web
import configparser
import re
import config as cfg
from tabulate import tabulate
from colorama import Fore, Style

config = configparser.ConfigParser()


def get_all_bagrut_data(years=None, sort=True):
    """
    gets the all bagrut exams according the requested years in a table
    each run the requested data saves, if the new data modified in compare of the previous data, the exam name will be colored as yellow.

    :param years: years of the requested exams ("2021, "2022") (could be also not transferred, that would be interpreted as all years)
    :param sort: sort grades by year of the exam (if multiple years selected - you can enable sorting option)
    :return: table of 'subject | year grade | bagrut grade | final grade' which can be printed
    """
    if cfg.mashov["username"] == "" or cfg.mashov["password"] == "" or cfg.mashov["semel"] == "" or cfg.mashov["year"] == "":
        print(Fore.RED + "\n[ERROR] Please fill up the config.py file!\n" + Style.RESET_ALL)
        return

    print("\n" + "[*] Username: " + cfg.mashov["username"] + "\n")

    if years is None:
        years_array = None
    else:
        years_array = years.replace(' ', '').split(',')  # remove spaces "2023, 2024" -> "2023,2024" in order to split it into array for easy usage

    pattern = r"\s*\(.*\)"
    url = web.BASEURL + "bagrut/grades"
    response = requests.request("GET", url, data=web.payload(), headers=web.get_header('GET'))

    if response.text == "":
        print(Fore.RED + "\n[ERROR] Wrong credentials in config.py file\n" + Style.RESET_ALL)
        return
    else:
        print(Fore.GREEN + "[SUCCESS] Logged in\n" + Style.RESET_ALL)

    bagrut_grades = json.loads(response.text)
    data = []

    last_data = _extract_data()

    for grade in bagrut_grades:
        if ("shnaty" in grade) or ("test" in grade) or ("final" in grade):
            if years_array is None or str(grade["moed"])[0:4] in years_array:

                modified_name = f"({grade['semel']})  " + re.sub(pattern, "", grade['name']) + (" (ב)" if str(grade['moed'])[4:6] == "08" else "") +  Fore.MAGENTA + f"  [{str(grade['moed'])[0:4]}]" + Style.RESET_ALL

                year_grade = _set_grade_color(str(grade.get('shnaty', "-")))
                test_grade = _set_grade_color(str(grade.get('test', "-")))
                final_grade = _set_grade_color(str(grade.get('final', "-")))

                if _grade_modified_or_added(modified_name, year_grade, test_grade, final_grade, last_data):
                    modified_name = Fore.YELLOW + modified_name + Style.RESET_ALL

                data.append([modified_name, year_grade, test_grade, final_grade])

    _save_data(data)

    if sort:
        data = sorted(data, key=lambda x: int(re.search(r'\[(\d+)\]', x[0]).group(1)))

    return tabulate(data, headers=["שם", "מגן", "בגרות", "סופי"], tablefmt="pretty")


def _grade_modified_or_added(name, shnaty, test, final, prev_data):
    different = True

    for grade in prev_data:
        if re.sub("\033\[[0-9;]*m", "", grade[0]) == re.sub("\033\[[0-9;]*m", "", name):  # compare the names without any colors comparing (it could be same name but newly added (colored yellow))
            if grade[1] == shnaty:  # compare the grades without removing the colors this is because if the colors are different - the grade also
                if grade[2] == test:  # ""
                    if grade[3] == final:  # ""
                        different = False  # !! SAME !!
                        break

    return different


def _set_grade_color(grade):
    FAIL_GRADE = (0, 55)  # 0 - 55
    LOW_GRADE = (55, 65)  # 55 - 65
    HIGH_GRADE = (90, 100)  # 90 - 100

    if grade == '-':  # no grade
        grade = Fore.CYAN + grade + Style.RESET_ALL
    else:
        if FAIL_GRADE[0] <= int(grade) <= FAIL_GRADE[1]:  # 0 - 55
            grade = Fore.RED + grade + Style.RESET_ALL
        elif LOW_GRADE[0] <= int(grade) <= LOW_GRADE[1]:  # 55 - 65
            grade = Fore.YELLOW + grade + Style.RESET_ALL
        elif HIGH_GRADE[0] <= int(grade) <= HIGH_GRADE[1]:  # 90 - 10
            grade = Fore.GREEN + grade + Style.RESET_ALL
        else:
            grade = Style.RESET_ALL + grade + Style.RESET_ALL  # not matches any color group

    return grade


def _extract_data():
    config.read("config.ini", encoding="utf-8")

    if config.has_section("data"):
        # Extract the value as a string from the configuration
        value_str = config.get("data", "last_data")

        # Convert the string back to a list
        return eval(value_str)
    else:
        return ""


def _save_data(data):
    config["data"] = {"last_data": data}

    # Write the configuration to a file
    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)
