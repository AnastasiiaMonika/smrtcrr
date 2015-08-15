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

#professions = {
#  "Java developer": ["Java", "Algorithms", "Probability theory", "JVM". "OOP"],
#  "Database Administrator": ["Databases", "Logical thinking", "Probability theory", "DBMS"], 
#  "Project manager": ["Algorithms", "Leadership"],
#  "Back-end developer": ["PHP", "JavaScript", "Python", "Node.js"],
#  "Front-end developer": ["CSS", "HTML", "JavaScript". "Design"],
#  "Web-designer": ["Photoshop", "CSS", "Paint", "HTML"],
#  "IOS developer": ["Algorithms", "Swift", "Objective-C", "IOS"],
#  "C# developer": ["C#", "Algorithms", "Probability theory", "ASP.NET"],
#  "Android developer": ["Java", "XML", "Android", "Algorithms"],
#  "Embedded developer": ["C", "Embedded", "Linux", "Algorithms", "Operating System"],
#  "Business Analyst": ["Analysis", "Optimisation", "Data Mining", "Optimizations", "Risk Analytics"],
#  "Graphic Design" :["infotech,arts",  "Adobe Acrobat Adobe Creative Suite  Flash Illustrator InDesign  Photoshop Aesthetics  Analytical Skills Creativity Skills CSS Dreamweaver Microsoft Excel HTML  Layout  Creative Writing  Typography
#}

#links = {
#  "Java developer": "https://www.youtube.com/playlist?list=PLBD5381FE500534C0",
#  "Database Administrator": "https://www.youtube.com/watch?v=dMkwFzRgxZY",
#  "Project manager" : "https://www.oppmi.com/project-management-training-videos.cfm",
#  "Back-end developer" : "https://www.youtube.com/watch?v=HYMvYYOhuYU",
#  "Front-end developer": "https://www.youtube.com/watch?v=Lsg84NtJbmI" ,
#  "Web-designer": "https://www.youtube.com/user/GoogleWebDesigner",
#  "IOS developer": "https://www.youtube.com/watch?v=mDgNwmHMaDo&list=PLnxBrInqFEs4d3SwS7HctEgg9Rhwe0tZT",
#  "C# developer": "https://www.youtube.com/watch?v=I7kDw0VbavQ&list=PL8DF7EE1104C11862",
#  "Android developer": "https://www.youtube.com/watch?v=SUOWNXGRc6g&list=PL2F07DBCDCC01493A",
#  "Embedded developer": "https://www.youtube.com/watch?v=uLD6dRim67A&list=PLX8CzqL3ArzXUvzzRdfuS-Dc50Hy0hpmR",
#  "Business Analyst": "https://www.youtube.com/watch?v=wHwfsH4WLD0",
#}

#link_name = "https://ua.linkedin.com/pub/anastasiia-matviichuk/103/895/aa7"
#link_name = "https://ca.linkedin.com/in/romanko"
#link_name = "https://vk.com"
link_name = "https://www.linkedin.com/profile/view?id=AAEAAAC19LgByHNr7FNDMhGz3de_IP1aj_JaA3o&authType=name&authToken=oyiR&trk=prof-sb-browse_map-name"
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

    def get_local_link(self, url):
      print 'Mi-mi'
      # parser = linkedinlogin.LinkedInParser(username, password)
      cj = cookielib.MozillaCookieJar(linkedinlogin.cookie_filename)
      cj.load()
      self._br.set_cookiejar(cj)
      content = self._br.open(url).read()
      result = map(lambda x: x.text.encode('utf-8'),
        BeautifulSoup(content, 'html.parser').find_all('a', 'view-public-profile'))
      if result == []:
       #  raise ValueError("No skills found")
        print 'No public link found'
        exit(0)
      return result[0]


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
      #function found not locat link
      link_name = crawler.get_local_link(link_name)
    profs = get_profession(crawler.get_skills(link_name))
    print profs
    top_prof = sort_skills(profs)[:3]
    print top_prof
    print 'For more information, please, click on name of profession:'
    for prof in top_prof:
      print 'You can be: <a href="https://www.coursera.org/courses?categories=' + coursera_link[prof] + '">' + prof + '</a>'
  else:
    print 'Sorry, this link is not from Linkedin'