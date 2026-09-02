import requests, yaml, json, base64, uuid, time, os
import datetime as dt

# -----INFO-----
# 
# NON-FUNCTIONAL VERSION OF HSL - DO NOT RUN / COMPILE
#
# Code is messy and probably incredibly inefficent as I'm not a professional
# Hopefully with enough updates it can be cleaned up as I learn more
# Please bear in mind, this is my first OOP based project
#
# Comments may refer to classes in this format "ClassName#property..." (The Paper API documentation refers to methods this way so I thought I may as well do that too)
# The use of a "#" instead of a "." is used to represent that this is a property being accessed from an instance of that class
# "instanceName.property..." where "instanceName" is an instance of the "ClassName" class is an example of how such comments can be interpreted and used in code
# The Paper API docs do the same thing so I may as well too
#
# To download island images, TheMysterys IslandCDN is used for now until a better solution is found
# Note: this service enforces undocumented rate limiting most likely something to do with cloudflare so images may occasionally take a while to download
# To avoid unauthorised distribution of MCC Island/Noxcrew assets, these icons will never be packaged with the program and will be downloaded and overwritten as needed
# IslandCDN itself will be shut down indefinitley at an unknown but not too distant date and will become unusable as a result
# This version of HSL will not work once this happens
#
# -----MODULE PURPOSES-----
#
# no idea why i made this list
#
# requests - Makes http requests to both the MCC Island and Mojang APIs
# yaml (PyYaml) - reads, writes and converts .yml files to other formats including json and python dictionaries
# json - converts json strings into python dictionaries and vice versa
# base64 - used once for decoding base64 information returned by the mojang API
# os - primarily used for generating file paths
# uuid - used only to add hyphens to a uuid in the correct places as the mojang API returns uuids without them while the MCCI API requires them
# time - used to add a delay between statistic refreshes, this pauses the main thread for the given time so will not be used when Harbor moves to a Tkinter GUI
# datetime - dt alias applied on import. provides the current date and time to be added at the beginning of

class Log:

    def createLogFile():
        with open(os.path.join(Program.paths.resources, "logs", "latest.log"), "w") as stream:
            stream.write(f"Log created at {dt.datetime.now().isoformat("T")}.\n")

    mem = ""

    def output(content: str, processID: str):
        line = f"[{dt.datetime.now().isoformat("T")}] [{processID}] {content}"
        Log.mem += f"{line}\n"
        print(line)

    def saveMem():
        with open(os.path.join(Program.paths.resources, "logs", "latest.log"), "a") as stream:
            stream.write(Log.mem)
        Log.mem = ""

# Will eventually be made redundant
class MacroFunctions:
    # Contains various functions often required by multiple parts of the program

    # Takes either a dictionary or json string as an param and the number of spaces per indent as an optional param with a default value of 4
    # Returns a string in a format with better readability
    # Intended as a development utility, won't be included in production builds
    @staticmethod
    def prettyPrint(unformattedJson, indent: int = 4) -> str:
        # sort based on input type
        if type(unformattedJson) == dict:

            return json.dumps(unformattedJson, indent=indent)
        
        elif type(unformattedJson) == str:

            return json.dumps(json.loads(unformattedJson), indent=indent)

        # warn when neither of the correct types are present
        else:

            raise TypeError(f"Expected type 'str' or type 'dict' but type '{str(type(unformattedJson)).split("'")[1]}' was present")

    # Output to terminal with other useful information
    # Deprecated
    # Use Log class
    @staticmethod
    def log(output: str, processID: str):

        # Concatenates output information with an RFC-3339 compliant date time and the process id
        print(f"[{dt.datetime.now().isoformat("T")}] [{processID}] {output}")

    # recursively builds a directory system defined by a dictionary in the provided root folder
    @staticmethod
    def buildDirectoryTree(tree: dict, rootDirectory: str):
        # builds directories in root by iterating over first level
        for k, v in tree.items():
            os.makedirs(os.path.join(rootDirectory, k))
            # pass second level recursively if it exists
            if type(v) == dict:
                MacroFunctions.buildDirectoryTree(v, os.path.join(rootDirectory, k))
        Log.output(f"Built directories in {rootDirectory}.", "File Manager")

# Used to make requests to an API
# Will make more sense with the introduction of support for other minecraft server's APIs
#
# For the format of the MCC Island API, the headers dictionary is constant and will only ever need to be changed if a new API key is required
# The API key should be the only header that can be changed by the user
#
# To implement:
#     - Mojang's API should also have its own instance of this class
#     - Maybe not
class API:

    def __init__(self, url: str, headers: dict):

        self.url = url
        self.headers = headers

    def sendRequest(self, jsonTransport: dict = {}) -> dict:
        # ensure api key actually exists, raise error if not
        if self.headers["X-API-Key"] != None:
            # make a store requests as a dict
            r = requests.post(self.url, headers = self.headers, json=jsonTransport).json()
            # build and save last query to json
            lastQuery = {
                "timestamp": dt.datetime.now().isoformat("T"),
                "query": jsonTransport,
                "response": r
            }
            with open(os.path.join(Program.paths.resources, "application", "lastQuery.json"), "w") as stream:
                stream.write(json.dumps(lastQuery, indent=4))
            Log.output("Saved query.", "API client")
            return r
        else:
            raise TypeError("API-Key has not been set! This is an internal error. Consider making a bug report.")

class Program:

    # Stores paths and un-resolved directory trees needed by the program
    class paths:
        # points to relative resources
        resources = os.path.join(os.getcwd(), "resources")
        # points to labels inside resources
        # also relative
        label = os.path.join(resources, "labels")

        # the structure for the labels directory
        # build by Program.initLabelResources() among other things that this function does
        labelDirectoryTree = {
            "labels": {
                "txt": {
                    "crownLevel": {
                        "overall": None,
                        "fishing": None,
                        "style": None,
                        "skillTrophyData": None
                    },
                    "program": None
                },
                "png": {
                    "crownLevel": {
                        "overall": None,
                        "fishing": None,
                        "style": None,
                    },
                    "program": None
                }
            }
        }

    def initLabelResources():
        # create labels directory if it doesn't exist
        if not os.path.exists(Program.paths.label):
            MacroFunctions.buildDirectoryTree(
                Program.paths.labelDirectoryTree,
                Program.paths.resources
            )

        # status file
        with open(os.path.join(Program.paths.label, "txt", "program", "dataStatus.txt"), "w") as stream:
            stream.write("Offline")
        # list of stat files to create per trophy type
        toCreate = [
            "level",
            "levelObtainable",
            "levelPercentage",
            "nextLevel",
            "nextLevelObtained",
            "nextLevelObtainable",
            "nextLevelPercentage",
            "evolution",
            "evolutionObtainable",
            "evolutionPercentage",
            "nextEvolution",
            "nextEvolutionObtained",
            "nextEvolutionObtainable",
            "nextEvolutionPercentage",
            "trophiesObtained",
            "trophiesObtainable",
            "trophiesPercentage"
        ]
        # create by iterating over types
        for file in toCreate:
            for i in ["overall", "fishing", "style"]:
                with open(os.path.join(
                    Program.paths.label,
                    "txt",
                    "crownLevel",
                    i,
                    f"{file}.txt"
                ), "w") as stream:
                    stream.write("")
        # list of files for skill trophies specifically due to a lack of level for this type
        toCreate = [
            "trophiesObtained",
            "trophiesObtainable",
            "trophiesPercentage"
        ]
        for file in toCreate:
            with open(os.path.join(
                Program.paths.label,
                "txt",
                "crownLevel",
                "skillTrophyData",
                f"{file}.txt"
            ), "w") as stream:
                stream.write("")
        Log.output("Created text files.", "Labels")
        # make image files
        # tuple guide
        # index 0: subdirectory
        # index 1: list of file paths to save image to as some are duplicate 
        toCreate = [
            ("icons/crowns/0", [
                os.path.join("crownLevel", "overall", "evolution.png"),
                os.path.join("crownLevel", "overall", "nextEvolution.png")
            ]),
            ("fishing/level/0", [
                os.path.join("crownLevel", "fishing", "evolution.png"),
                os.path.join("crownLevel", "fishing", "nextEvolution.png")
            ]),
            ("icons/style_level/0", [
                os.path.join("crownLevel", "style", "evolution.png"),
                os.path.join("crownLevel", "style", "nextEvolution.png")
            ])
        ]
        # iterate
        for icon in toCreate:
            imageBytes = requests.get(f"https://islandcdn.themysterys.com/{icon[0]}.png").content
            for destination in icon[1]:
                with open(os.path.join(
                    Program.paths.label,
                    "png",
                    destination
                ), "wb") as stream:
                    stream.write(imageBytes)
        Log.output("Created image files.", "Labels")

    # config serialised as a dict
    config = None
    # reads and serialises config.yml
    def loadConfig():
        with open(os.path.join(
            Program.paths.resources,
            "config.yml"
        ), "r") as stream:
            Program.config = yaml.safe_load(stream)
    # startup json serialised as dict
    startup = None
    # reads and serialises application/startup.json
    def loadStartup():
        with open(os.path.join(
            Program.paths.resources,
            "application",
            "startup.json"
        ), "r") as stream:
            Program.startup = json.loads(stream.read())
    # reserialises startup dict and stores back in application/startup.json
    def saveStartup():
        with open(os.path.join(
            Program.paths.resources,
            "application",
            "startup.json"
        ), "w") as stream:
            stream.write(json.dumps(Program.startup, indent=4))
        Log.output("Saved startup information.", "Thread")
    # requests, loads, and stores minecraft account data
    def storeAccountData() -> bool:
        # validation needs cleaning up
        # for now this avoids unnecessary requests
        if len(Program.config["user"]["name"]) > 16 or len(Program.config["user"]["name"]) < 3:
            raise ValueError("Username is invalid! Please set a valid username.")
        try:
            r = requests.get(f"https://api.mojang.com/minecraft/profile/lookup/name/{Program.config["user"]["name"]}").json()
        except:
            raise ValueError("Username is invalid! Please set a valid username.")
        # ensures startup flags has actually been loaded
        if (type(Program.startup) == dict):
            Program.startup["last-user"] = {
                "name": r["name"],
                "uuid": str(uuid.UUID(r["id"])),
                "moj-uuid": r["id"]
            }
            Program.saveStartup()
            return True
        else:
            return False

    def setApiKey():
        MccIslandAPI.api.headers["X-API-Key"] = Program.config["user"]["API-Key"]

    # controls startup sequence of the program
    def executeStartup():
        Log.createLogFile()
        Log.output("Created log file.", "Thread")
        # load necessary files
        Program.loadConfig()
        Program.loadStartup()

        Log.output("Loaded external files.", "Thread")

        resetTime = Program.config["program"]["resetTime"]
        # This check will clamp reset time or set to a recommended time if the provided value lies out of range
        if (type(resetTime) != int) or (resetTime < 4) or (resetTime > 45):
            raise ValueError(f"Invalid reset time! Reset time must be an integer (whole number) between 4 and 45. Not a {type(resetTime)} of value {resetTime}")
        if type(Program.config["user"]["API-Key"]) != str:
            raise ValueError(f"Invalid api key! Generate a valid api key by logging in to https://gateway.noxcrew.com and pasting it here.")

        # check whether program resources has to by initialised / reset
        # if username has changed since last session then a reset will occur to avoid innaccurate data in labels
        if (Program.startup["last-user"] == None) or (Program.startup["last-user"]["name"].lower() != Program.config["user"]["name"].lower()):

            Program.storeAccountData()
            Log.output("Loaded/updated account data.", "Thread")
            Program.initLabelResources()
            Log.output("Initialised label resources.", "Thread")

        # loads and validates the user's api-key
        Program.setApiKey()
        MccIslandAPI.validateApiKey()
        Log.output("Set and validated API key.", "Thread")

        # builds and resolves modular query body based on config.yml query settings
        MccIslandAPI.resolvedQueryBody = MccIslandAPI.buildQueryBody()
        Log.output("Built GraphQL query from config file.", "Thread")
        Log.saveMem()

    def mainLoop():
        if MccIslandAPI.resolvedQueryBody != None:
            Log.output("Attempting query.", "Thread")
            initResponse = MccIslandAPI.api.sendRequest({"query": MccIslandAPI.resolvedQueryBody, "variables": {"uuid": Program.startup["last-user"]["uuid"]}})
            Log.output("API response received.", "Thread")
            fullResponse = Program.addMoreData(initResponse)
            Log.output("Computed additional data.", "Thread")
            Program.updateLabelData(fullResponse["data"]["player"])
            Log.output("Updated label content.", "Thread")
        else:
            raise ValueError("No query to send! This is an internal error. Consider creating a bug report.")

    # pass dict in data.player
    def updateLabelData(data: dict):

        # links data to similar grouped data which can be referenced
        # key: the name of the field in config.yml
        # index 0: name of level data object in api response
        # index 1: name of trophy object in api response
        # index 2: name of directory where the data will be stored
        # index 3: subdirectory to concatenate to url "https://islandcdn.themysterys.com/" 
        key = {
            "overallData": ("levelData", "overallTrophies", "overall", "icons/crowns"),
            "fishingData": ("fishingLevelData", "fishingTrophies", "fishing", "fishing/level"),
            "styleData": ("styleLevelData", "styleTrophies", "style", "icons/style_level"),
            "skillTrophies": (None, "skillTrophies", "skillTrophyData", None)
        }

        # loop through trophy types in config
        for k, v in Program.config["getData"]["trophyLeveling"].items():
            # only if this type is on should it be updated
            if v:
                # check if this type has level data
                if key[k][0] != None:
                    # moves focus to the relevant object
                    focus = data["crownLevel"][key[k][0]]
                    # tuple guide
                    # index 0: the relevant file
                    # index 1: the location in the focus data
                    toUpdate = (
                        ("level", focus["level"]),
                        ("levelObtainable", focus["levelProgress"]["obtainable"]),
                        ("levelPercentage", focus["levelProgress"]["percentage"]),
                        ("nextLevel", focus["nextLevel"]),
                        ("nextLevelObtained", focus["nextLevelProgress"]["obtained"]),
                        ("nextLevelObtainable", focus["nextLevelProgress"]["obtainable"]),
                        ("nextLevelPercentage", focus["nextLevelProgress"]["percentage"]),
                        ("evolution", focus["evolution"]),
                        ("evolutionObtainable", focus["evolutionProgress"]["obtainable"]),
                        ("evolutionPercentage", focus["evolutionProgress"]["percentage"]),
                        ("nextEvolution", focus["nextEvolution"]),
                        ("nextEvolutionObtained", focus["nextEvolutionProgress"]["obtained"]),
                        ("nextEvolutionObtainable", focus["nextEvolutionProgress"]["obtainable"]),
                        ("nextEvolutionPercentage", focus["nextEvolutionProgress"]["percentage"]) 
                    )
                    # saving by iteration
                    for stat in toUpdate:
                        with open(os.path.join(
                            Program.paths.label,
                            "txt",
                            "crownLevel",
                            key[k][2],
                            f"{stat[0]}.txt"
                        ), "w") as stream:
                            stream.write(str(stat[1]))
                # check if this type has trophy data
                if key[k][1] != None:
                    #changes focus
                    focus = data["crownLevel"][key[k][1]]
                    # same as last
                    toUpdate = (
                        ("trophiesObtained", focus["obtained"]),
                        ("trophiesObtainable", focus["obtainable"]),
                        ("trophiesPercentage", focus["percentage"])
                    )
                    # iteration
                    for stat in toUpdate:
                        with open(os.path.join(
                            Program.paths.label,
                            "txt",
                            "crownLevel",
                            key[k][2],
                            f"{stat[0]}.txt"
                        ), "w") as stream:
                            stream.write(str(stat[1]))
                # if this type has icons attached
                if key[k][3] != None:
                    focus = data["crownLevel"][key[k][0]]
                    # get current and next evolution
                    evolution = requests.get(f"https://islandcdn.themysterys.com/{key[k][3]}/{focus["evolution"]}.png").content
                    nextEvolution = requests.get(f"https://islandcdn.themysterys.com/{key[k][3]}/{focus["evolution"] + 1}.png").content
                    # saves to files
                    with open(os.path.join(Program.paths.label, "png", "crownLevel", key[k][2], "evolution.png"), "wb") as stream:
                        stream.write(evolution)
                    with open(os.path.join(Program.paths.label, "png", "crownLevel", key[k][2], "nextEvolution.png"), "wb") as stream:
                        stream.write(nextEvolution)

    def addMoreData(data: dict) -> dict:
        # links level data object to corresponding trophy data object
        dataParallels = {
            "levelData": "overallTrophies",
            "fishingLevelData": "fishingTrophies",
            "styleLevelData": "styleTrophies"
        }
        # copies data to prevent accidental override
        dataToProcess = data.copy()
        # are any crown level options enabled
        if "crownLevel" in dataToProcess["data"]["player"]:
            # iterate over all crown data in response
            for k, v in dataToProcess["data"]["player"]["crownLevel"].items():
                # all level data object's keys end with "Data"
                # this allows isolated processing
                if k.endswith("Data"):
                    # links trophy data so that it can be accessed where needed for calculations
                    parallelsTrophy = dataToProcess["data"]["player"]["crownLevel"][dataParallels[k]]

                    # nextLevel is clamped to 110 and nextEvolution is clamped to 10
                    # actually both reset to 0 and loop backwards
                    # this is a future proof failsafe as evolution icons beyond 10 don't exist on the cdn
                    # nor in the resource pack
                    # Note: there are not enough obtainable trophies to get beyond evolution 8 overall
                    v["nextLevel"] = (v["level"] + 1) % 111
                    v["nextEvolution"] = (v["evolution"] + 1) % 11
                    v["nextLevelProgress"]["percentage"] = f"{round(v["nextLevelProgress"]["obtained"] / v["nextLevelProgress"]["obtainable"] * 100, 1)}%"
                    v["levelProgress"] = {
                        "obtainable": parallelsTrophy["obtained"] - v["nextLevelProgress"]["obtained"] + v["nextLevelProgress"]["obtainable"]
                    }
                    v["levelProgress"]["percentage"] = f"{round(parallelsTrophy["obtained"] / v["levelProgress"]["obtainable"] * 100, 1)}%"
                    v["nextEvolutionProgress"] = {
                        "obtained": ((v["level"] % 10) * v["nextLevelProgress"]["obtainable"]) + v["nextLevelProgress"]["obtained"],
                        "obtainable": v["nextLevelProgress"]["obtainable"] * 10
                    }
                    v["nextEvolutionProgress"]["percentage"] = f"{round(v["nextEvolutionProgress"]["obtained"] / v["nextEvolutionProgress"]["obtainable"] * 100, 1)}%"
                    v["evolutionProgress"] = {
                        "obtainable": v["nextLevelProgress"]["obtainable"] * (v["nextEvolutionLevel"] - v["level"]) + parallelsTrophy["obtained"] - v["nextLevelProgress"]["obtained"]
                    }
                    v["evolutionProgress"]["percentage"] = f"{round(parallelsTrophy["obtained"] / v["evolutionProgress"]["obtainable"] * 100, 1)}%"
                # all trophy data object's keys end in "Trophies"
                if k.endswith("Trophies"):
                    v["percentage"] = f"{round(v["obtained"] / v["obtainable"] * 100, 1)}%"

        return dataToProcess

# contains part of a GraphQL query
class QueryBlock:

    # top and bottom will be placed outside of any internal query blocks to maintain query structure
    # fragments are always appended after the rest for congruency with GraphQL fragment definition
    def __init__(
            self,
            top: str = "",
            bottom: str = "",
            mainBody: list[QueryBlock] | None = None,
            fragments: list[str] | None = None,
    ):

        self.top = top
        self.bottom = bottom
        # Both of these are assigned their own lists
        # Previously a logic error created infinite references to other query blocks
        # this solution has fixed that
        self.mainBody = [] if mainBody is None else mainBody
        self.fragments = [] if fragments is None else fragments

    # Recursively builds the content of a query block into a single string
    def resolve(self) -> str:

        resolved = self.top
        for queryBlock in self.mainBody:
            # recursively builds inner blocks
            resolved += queryBlock.resolve()
        resolved += self.bottom
        for fragment in self.fragments:
            resolved += fragment

        Log.output("Resolved query body to string. (This may appear multiple times)", "Query handler")

        return resolved

# I will probably merge this into API class once i can figure out a way to do it
class MccIslandAPI:

    api = API(

        url = "https://api.mccisland.net/graphql",

        headers = {
            # API-Key is set during startup
            # and requests made before this is done will raise an error before the actual request is sent
            # flagged as an internal error which it is if this ever happens
            "X-API-Key": None,
            "Content-Type": "application/json",
            "User-Agent": "Harbor Stream Labels (Discord/@whatcheeseburger) Python-HttpClient"       
        }
    )

    def buildQueryBody() -> str:
        # includes username in query so that empty queries do not throw an error
        mainBody = QueryBlock(
            """
query player($uuid: UUID!) {
    player(uuid: $uuid) {
        username""",
            """
    }
}"""
        )

        crownLevelBlock = QueryBlock(
            """
        crownLevel {""",
            """
        }"""
        )

        crownLevelAvailableBlocks = {
            "overallData": QueryBlock(
                """
                levelData {
                    ...levelDataFragment
                }
                overallTrophies: trophies {
                    ...trophyDataFragment
                }"""
            ),
            "fishingData": QueryBlock(
                """
                fishingLevelData {
                    ...levelDataFragment
                }
                fishingTrophies: trophies(category: ANGLER) {
                    ...trophyDataFragment
                }"""
            ),
            "styleData": QueryBlock(
                """
                styleLevelData {
                    ...levelDataFragment
                }
                styleTrophies: trophies(category: STYLE) {
                    ...trophyDataFragment
                }"""
            ),
            "skillTrophies": QueryBlock(
                """
                skillTrophies: trophies(category: SKILL) {
                    ...trophyDataFragment
                }"""
            )
        }

        fragments = {
            "crownLevel": """
fragment levelDataFragment on LevelData {
    level
    evolution
    nextEvolutionLevel
    nextLevelProgress {
        obtained
        obtainable
    }
}
fragment trophyDataFragment on TrophyData {
    obtained
    obtainable
}"""
        }

        crownLevelAdded = False
        Log.output("Reading query config.", "Query handler")
        for category, value in Program.config["getData"]["trophyLeveling"].items():
            if value:
                crownLevelAdded = True
                crownLevelBlock.mainBody.append(crownLevelAvailableBlocks[category])
        if crownLevelAdded:
            mainBody.mainBody.append(crownLevelBlock)
            mainBody.fragments.append(fragments["crownLevel"])
        Log.output("Arranged query body.", "Query handler")
        return mainBody.resolve()

    resolvedQueryBody = None

    def validateApiKey():
        Log.output("Attempting test request.", "API client")
        r = MccIslandAPI.api.sendRequest(
            {
                "query": """
query availableQueueTypes {
    availableQueueTypes
}"""
            }
        )

        if "message" in r:
            if r["message"].lower() == "unauthorized":
                raise ValueError("API Key is invalid! Please set a valid API Key")
        else:
            Program.startup["api-key-valid"] = True
            Program.saveStartup()

def main():

    Program.executeStartup()
    Log.output("Starting main loop.", "Thread")
    """while True:
        Program.mainLoop()
        # wait a configured number of minutes between data updates
        # recommended is 15
        time.sleep(Program.config["program"]["resetTime"] * 60)"""

if __name__ == "__main__":
    main()