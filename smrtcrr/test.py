# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import mechanize
import csv
import sys
import requests
import linkedinlogin
import cookielib

username = "mariamforminin@gmail.com"
password = "mariam000"

def get_professions(path):
  with open(path, 'rb') as f:
    reader = csv.reader(f)
    return { row[0].strip() : filter(lambda x: x != '', map(lambda x: x.strip(), row[1:])) for row in reader }

professions = get_professions('skills.csv')

def get_coursera(path):
  with open(path, 'rb') as f:
    reader = csv.reader(f)
    return { row[0].strip() : row[1].strip() for row in reader }

coursera_link = get_coursera('coursera.csv')

#without skills, public link:
#link_name = "https://ua.linkedin.com/pub/anastasiia-matviichuk/103/895/aa7" 
#with skills, public link:
#link_name = "https://ca.linkedin.com/in/romanko"
#no access, local link:
#link_name = "https://www.linkedin.com/profile/view?id=AAIAAAiuDSYBeO6kwAcbQL_Me5u61Fl8vZk3W54&trk=nav_responsive_tab_profile_pic" # Vitalii
#another wab page:
#link_name = "https://vk.com"
#with skills, local link:
link_name = "https://www.linkedin.com/profile/view?id=AAEAAAC19LgByHNr7FNDMhGz3de_IP1aj_JaA3o&authType=name&authToken=oyiR&trk=prof-sb-browse_map-name" # Romanko local
#link_name = "https://ca.linkedin.com/pub/kyle-macdonald/46/ba0/5b"

class Crawler:
    def __init__(self):
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-Agent', "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36")]

        self._br = br

    def get_skills(self, url):
        content = self._br.open(url).read()
        result = map(lambda x: x.text.encode('utf-8'),
              BeautifulSoup(content, 'html.parser').find_all('a', 'endorse-item-name-text'))
        if result == []:
        #    raise ValueError("No skills found")
          print 'No skills found'
          exit(0)
        return result

    def login(self):
      # parser = linkedinlogin.LinkedInParser(username, password)
      cj = cookielib.MozillaCookieJar(linkedinlogin.cookie_filename)
      cj.load()
      self._br.set_cookiejar(cj)


def get_profession(skills):
    def match(prof_skills):
        count = 0
        for skill in skills:
            for prof_skill in prof_skills:
                if skill.lower() == prof_skill.lower():
                    count += 1
        return float(count) / len(prof_skills)

    return { profession: match(prof_skills) for profession, prof_skills in professions.items()}


def sort_skills(d):
    return sorted(d, key=d.get, reverse=True)

if __name__ == '__main__':
  crawler = Crawler()
  if "linkedin" in link_name:
    if "profile/view" in link_name:
      crawler.login()
    profs = get_profession(crawler.get_skills(link_name))
    print profs
    top_prof = sort_skills(profs)[:3]
    print top_prof
    print 'For more information, please, click on name of profession:'
    for prof in top_prof:
      print 'You can be: <a href="https://www.coursera.org/courses?categories=' + coursera_link[prof] + '">' + prof + '</a>'
  else:
    print 'Sorry, this link is not from Linkedin'