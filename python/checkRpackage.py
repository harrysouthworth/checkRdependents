def unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def runRCMDcheck(path="tarballs"):
    """Run R CMD check on all tar.gz files found in path"""

    from os import listdir
    from os import system
    from os.path import isfile, join

    allfiles = [f for f in listdir(path) if isfile(join(path, f))]
    files = [f for f in allfiles if f[-7:] == ".tar.gz"]

    for f in files:
        print("Checking " + f)
        cmd = "cd " + path + "; R CMD check " + f + " > output.log"
        system(cmd)


def lookForProblems(path="tarballs"):
    """Find any instance of 'ERROR', 'WARNING' or 'NOTE' in the output of
       R CMD check"""

    from os import listdir
    from os.path import isfile, join
    
    dirs = [f for f in listdir(path) if not isfile(join(path, f))]

    outfile = open("checkRdependents.log", "w")

    for directory in dirs:
        s = "\n" + "*"*20 + " " + directory[:-7] + " " + "*"*20 + "\n"
        print(s)
        outfile.write(s)
        for file in ["/00install.out", "/00check.log"]:
            try:
                infile = open(path + "/" + directory + file)
                for line in infile:
                    if "ERROR" in line or "WARNING" in line or "NOTE" in line:
                        print(line)
                        outfile.write(line)
            except:
                print(file + " not found.")

def getDependents(package):
    """ Retrieve a package CRAN page and parse it to get a list of dependent
        packages. """
    
    from urllib import urlretrieve
    from bs4 import BeautifulSoup
    from string import join

    # Retrieve page, read it, turn into soup
    url = "http://cran.r-project.org/web/packages/" + package + "/index.html"
    localfile = "." + package + ".html"
    page = urlretrieve(url, localfile)
    page = open(localfile, "r").read()
    soup = BeautifulSoup("".join(page))

    # Grab the table of dependents
    deps = soup.find("table", {"summary" : "Package " + package + " reverse dependencies"})
    deps = deps.findAll("tr")[0] # First row
    deps = deps.findAll("a")
    deps = [str(d.text) for d in deps]
    
    print("Dependent packages:")
    print(join(deps, ", "))

    return(deps)

def getDependencies(package):
    """ Retrieve a package CRAN page and parse it to get a list of packages
        on which it depends. """
    
    from urllib import urlretrieve
    from bs4 import BeautifulSoup
    from string import join

    # Retrieve page, read it, turn into soup
    url = "http://cran.r-project.org/web/packages/" + package + "/index.html"
    localfile = "." + package + ".html"
    page = urlretrieve(url, localfile)
    page = open(localfile, "r").read()
    soup = BeautifulSoup("".join(page))

    # Grab the table of dependencies
    deps = soup.find("table", {"summary" : "Package " + package + " summary"})
    # Want to find the row with dependencies
    deps = deps.findAll("tr")[1]
    deps = deps.findAll("a")
    deps = [str(d.text) for d in deps]

    print(package + " dependencies:")
    print(join(deps, ", "))
    
    return(deps)


def getDependentTarNames(d):
    """ Take the names of some R packages and construct the name of
       the package source for the latest version. """

    from urllib import urlretrieve
    from bs4 import BeautifulSoup

    parturl = "http://cran.r-project.org/web/packages/"
    res = []

    for package in d:
        url = parturl + package + "/index.html"
        localfile = "." + package + ".html"

        page = urlretrieve(url, localfile)
        page = open(localfile, "r").read()
        soup = BeautifulSoup("".join(page))

        # Get the table with the file name in it
        smry = "Package " + package + " downloads"
        soup = soup.find("table", {"summary" : smry})
        soup = soup.findAll("tr")[0]
        soup = soup.findAll("a")

        for i in soup:
            res.append(str(i.text).strip())

    return(res)

def getPackages(packages, path="tarballs"):
    """ Download specified R package sources. """
    from urllib import urlretrieve
    
    parturl = "http://cran.r-project.org/src/contrib/"
    
    for package in packages:
        url = parturl + package
        print("Downloading " + package)
        urlretrieve(url, path + "/" + package)

def installPackages(packages, location):
    """ Use R CMD INSTALL to install a bunch of packages to the default library. """
    from os import system

    for package in packages:
        cmd = "cd " + location + "; R CMD INSTALL " + package
        system(cmd)

def checkDependents(package, path="tarballs",
                    dependencies="tarballs/dep", installDependencies=False,
                    download=True, check=True):
    """ Wrapper for other functions that identify, download and check
        dependent packages. Defaults to downloading fresh versions of
        dependent packages, behaviour which can be overridden by specifying
        download=False. """
    d = getDependents(package)
    dep = [getDependencies(i) for i in d]
    # dep is a list of lists. unlist it
    dep = [j for i in dep for j in i]
    dep = unique(dep)
    dep.remove(package)
    dep = getDependentTarNames(dep)

    if download:
        d = getDependentTarNames(d)
        getPackages(d)
        getPackages(dep, path=dependencies)

    if installDependencies:
        installPackages(dep, dependencies)

    if check:
        runRCMDcheck()
        lookForProblems()

