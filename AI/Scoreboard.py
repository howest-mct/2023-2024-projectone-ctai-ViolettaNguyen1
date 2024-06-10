import csv

class Score:
    def __init__(self, pscore, pchoreography_name, pdatetime) -> None:
        self.__score = int(pscore)
        self.__choreography_name = pchoreography_name
        self.__datetime = pdatetime

    # ********** property score - (getter only) ***********
    @property
    def score(self) -> int:
        """ The score property. """
        return self.__score
    
    # ********** property choreography_name - (getter only) ***********
    @property
    def choreography_name(self) -> type:
        """ The choreography_name property. """
        return self.__choreography_name
    
    # ********** property datetime - (getter only) ***********
    @property
    def datetime(self) -> type:
        """ The datetime property. """
        return self.__datetime
    
    def __str__(self) -> str:
        return f"Score: {self.score}, Choreography: {self.choreography_name}, Date: {self.datetime[:4]}/{self.datetime[4:6]}/{self.datetime[6:8]} {self.datetime[9:11]}:{self.datetime[11:13]}:{self.datetime[13:]}"  
    
    def __lt__(self, other):
        if isinstance(other, Score):
            if self.score < other.score:
                return True
        else:
            raise ValueError("There is an issue with comparing the scores...")

class Scoreboard:

    def read_scoreboard():
        file = r".\Files\performance_scores.csv"
        file = open(file, "r")
        reader = csv.reader(file)
        next(reader) # To skipp the column names
        
        list_scores = []
        for row in reader:
            score = Score(row[0],row[1],row[2])
            list_scores.append(score)
        return list_scores
    
    def print_top_k_scores(k: int):
        list_scores = Scoreboard.read_scoreboard()
        list_scores.sort(reverse=True)
        for i in range(k):
            print(f"\n{i+1}.", list_scores[i])
        

        
        