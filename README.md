# Jobbed - get your resume in any format

## About

The **problem**: I want my resume available as a nice pdf, on my personal
website and *maybe* in other formats (like github flavored Markdown). The result
MUST look like written exactly for given target.

## How to use

Install `zeromq/gsl`, put `jobbed_latex.gsl` to your `PATH` and run

```
gsl -script:jobbed_latex resume.xml
docker run -w /data -v $(pwd):/data -it --rm hiono/texlive pdflatex resume.tex
```

You will find the result PDF as `resume.pdf`.

And of course, feel free to use whatever Texlive installation as you want to :-)

## REST API

Note: this is WIP, no API stability is guaranteed atm

```
cd rest/
pipenv install
pipenv shell
python3 app.py
```

## TL;DR

It is a magic. You write one xml file, call the tool `gsl`, *et voilà !* We got
our files.

Schematically

    [template: TeX.gsl]    ----              ---->  [resume.tex]
                              |              |
                              ---->       ----
    [XML model of resume ] -------> [gsl]
                              ---->       ----
                              |              |
    [template: MD.gsl]     ----              ----> [resume.md]

## Solution

Split the data themselves from final (or intermediate) format. This is idea
floating around IT business for some time, however we still write our resumes
in the *tool du jour*. I've written it so many times, that I can't count that.

The solution to this problem is: [Model oriented
programming](https://github.com/zeromq/gsl#model-oriented-programming). This is
powerfull, but not commonly used way of solving the problems. It was explored a
lot by ZeroMQ community, so we know that investing an effort to develop a model
is worth the pain.

So `jobbed` simply defines some templates, which are gsl scripts. Those
iterates through input XML file and generating an output based on a template.
If you change the template, you change the final result. However resume model
renamins the same. If you want to change an output of an existing template.
Yes, you can! Templates resembles the intended output format with a few marks
of gsl language.

This way you can produce plain HTML, bootstrap-powered one or even make a fancy
Javascript game based on your resume data. The same way you can output exactly
the TeX (or LaTeX) file you want to.

## Wrong solutions

1. Do it **manually** - no way, we're developers
2. Write & convert - it's not going to look the same and of course it's easy to
   find a format we can't convert into
