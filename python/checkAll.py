def runRCMDcheck(path="tarballs"):
    """Run R CMD check on all tar.gz files found in path"""

    from os import listdir
    from os import system
    from os.path import isfile, join

    def istar(x):
        if x[-7:-1] == ".tar.gz":
            True
        else:
            False

    files = [f for f in listdir(path) if isfile(join(path, f))]
    
    for f in files:
        system("cd " + path + "; R CMD check " + f + "> output.log")

def lookForProblems(path="tarballs"):
    """Find any instance of 'ERROR', 'WARNING' or 'NOTE' in the output of
       R CMD check"""

    from os import listdir
    from os.path import isfile, join
    
    dirs = [f for f in listdir(path) if not isfile(join(path, f))]

    for directory in dirs:
        print("\n" + "*"*20 + " " + directory[:-7] + " " + "*"*20 + "\n")
        for file in ["/00install.out", "/00check.log"]:
            infile = open(path + "/" + directory + file)
            for line in infile:
                if "ERROR" in line or "WARNING" in line or "NOTE" in line:
                    print(line)

def getDependents(url="http://cran.r-project.org/web/packages/gbm/index.html",
                  tidy=True):
    """ Retrieve the gbm CRAN page and parse it to get a list of dependent
        packages. """
    
    from urllib import urlretrieve
    from bs4 import BeautifulSoup

    # Retrieve page, read it, turn into soup
    page = urlretrieve(url, ".gbm.html")
    page = open(".gbm.html", "r").read()
    soup = BeautifulSoup("".join(page))

    # Grab the table of dependents
    deps = soup.find("table", {"summary" : "Package gbm reverse dependencies"})
    deps = deps.findAll("tr")[0] # First row
    deps = deps.findAll("a")
    res = []
    for d in deps:
        res.append(d.text)             
    
    print("Dependent packages:")
    for d in res:
        print(d)

    if tidy:
        from os import system
        system("rm .gbm.html")

    return(d)

def getDependentTarNames(d):
    "" Take the names of some R packages and construct the name of
       the package source for the latest version. """

    

def getPackages(packages, path="tarballs"):
    """ Download specified R package sources. """
    from urllib import urlretrieve
    
    parturl = "http://cran.r-project.org/src/contrib/"
    
    for package in packages:
        package = parturl + package + ".tar.gz"
        urlretrieve(package, path)

def main(path="tarballs"):
    d = getDependents()
    getPackages(d)

main()

#runRCMDcheck()
#lookForProblems()
    

