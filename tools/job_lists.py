"""
MASSIVE JOB SITE LISTS (126+ TARGETS)
Used by SiteSearchTool and JobSearchTool to ensure huge coverage.
"""

# 1. CORE REMOTE BOARDS (30)
REMOTE_BOARDS = [
    "weworkremotely.com", "remoteok.com", "remotive.com", "himalayas.app",
    "jobspresso.co", "remote.co", "justremote.co", "workingnomads.com",
    "wearedevelopers.com", "landing.jobs", "nodesk.co", "citizenremote.com",
    "jobgether.com", "pangian.com", "skipthedrive.com", "virtualvocations.com",
    "authenticjobs.com", "dribbble.com/jobs", "behance.net/joblist",
    "arc.dev", "gun.io", "toptal.com", "hired.com", "vettery.com",
    "dailyremote.com", "remote.io", "outerjoin.us", "remotewoman.com", 
    "remotely.one", "remoteweekly.cc"
]

# 2. STARTUPS & TECH (40)
STARTUP_SITES = [
    "ycombinator.com/jobs", "wellfound.com", "angel.co", "startup.jobs",
    "startupers.com", "startups.com/jobs", "techstars.com/jobs", "f6s.com",
    "workatastartup.com", "builtin.com", "crunchboard.com", "mashable.com/jobs",
    "techcrunch.com/jobs", "ventureloop.com", "uncubed.com", "underdog.io",
    "betalist.com/jobs", "producthunt.com/jobs", "indiehackers.com", 
    "dev.to/listings", "hashnode.com/jobs", "stackoverflow.com/jobs",
    "github.com/jobs", "gitlab.com/jobs", "geekwork.com", "dice.com",
    "icrunchdata.com", "kdnuggets.com/jobs", "analyticsvidhya.com/jobs",
    "datasciencejobs.com", "ai-jobs.net", "python.org/jobs", "djangojobs.net",
    "golangprojects.com", "rustjobs.com", "scala-jobs.org", "functional.works-hub.com",
    "clojurejobboard.com", "elixirjobs.net", "rubyfs.com"
]

# 3. INTERNSHIPS (30)
INTERNSHIP_SITES = [
    "internships.com", "chegg.com/internships", "wayup.com", "ripplematch.com",
    "handshake.com", "intern.supply", "looksharp.com", "internqueen.com",
    "idealist.org", "coolworks.com", "aftercollege.com", "collegegrad.com",
    "collegerecruiter.com", "mediabistro.com", "usajobs.gov/students",
    "internshipfinder.com", "globalexperiences.com", "goabroad.com/intern-abroad",
    "iie.org", "culturalvistas.org", "ciee.org", "aiesec.org",
    "graduateland.com", "europlacement.com", "erasmusintern.org",
    "placement-uk.com", "ratemyplacement.co.uk", "milkround.com",
    "targetjobs.co.uk", "prospects.ac.uk"
]

# 4. FREELANCE (30)
FREELANCE_SITES = [
    "upwork.com", "freelancer.com", "fiverr.com", "guru.com", "peopleperhour.com",
    "toptal.com", "99designs.com", "dribbble.com/freelance-jobs", "behance.net/job-list",
    "servicecape.com", "designhill.com", "taskrabbit.com", "flexjobs.com",
    "solidgigs.com", "cloudpeeps.com", "contently.com", "skyword.com",
    "writeraccess.com", "textbroker.com", "constant-content.com", "crowdsource.com",
    "mturk.com", "clickworker.com", "microworkers.com", "remotetasks.com",
    "rev.com", "transcribeme.com", "gotranscript.com", "babbletype.com",
    "verbalink.com"
]

# 5. INDIA SPECIFIC (20)
INDIA_SITES = [
    "naukri.com", "monsterindia.com", "timesjobs.com", "shine.com",
    "instahyre.com", "hirist.com", "iimjobs.com", "bigshyft.com",
    "cutshort.io", "freshersworld.com", "jobriya.in", "sarkariresult.com",
    "freejobalert.com", "jagranjosh.com", "careerpower.in", "bankersadda.com",
    "adda247.com", "testbook.com", "gradeup.co", "unacademy.com"
]

ALL_DOMAINS = REMOTE_BOARDS + STARTUP_SITES + INTERNSHIP_SITES + FREELANCE_SITES + INDIA_SITES
