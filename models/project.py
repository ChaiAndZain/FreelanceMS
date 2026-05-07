from datetime import datetime

# possible statuses
STATUS_OPTIONS = ["Pending", "In Progress", "Completed", "Cancelled"]

class Project:
    """
    Project class for project data
    """

    # constructor
    def __init__(self, project_id, title, client_id, deadline,
                 hourly_rate, hours_worked, status, description=""):
        self.__project_id = project_id    # unique ID (P001, P002...)
        self.__title = title          # project ka naam
        self.__client_id  = client_id      # kis client  ka project hai
        self.__deadline  = deadline       # deadline (YYYY-MM-DD format)
        self.__hourly_rate  = float(hourly_rate)   # per ghante rate (USD mein)
        self.__hours_worked = float(hours_worked)  # kitne ghante kaam kiya
        self.__status= status   # Pending / In Progress / Completed
        self.__description  =description    # project ka brief description

    #  ------ getters -------------
    def get_id(self):           return self.__project_id
    def get_title(self):        return self.__title
    def get_client_id(self):    return self.__client_id
    def get_deadline(self):     return self.__deadline
    def get_hourly_rate(self):  return self.__hourly_rate
    def get_hours_worked(self): return self.__hours_worked
    def get_status(self):       return self.__status
    def get_description(self):  return self.__description

    #   ------------ etters ---------
    def set_title(self, t):         self.__title = t
    def set_deadline(self, d):      self.__deadline = d
    def set_hourly_rate(self, r):   self.__hourly_rate = float(r)
    def set_hours_worked(self, h):  self.__hours_worked = float(h)
    def set_status(self, s):        self.__status = s
    def set_description(self, d):   self.__description = d

    # ------- gross earning ---------------
    def gross_earning(self):
        # rate * hours = total kamai
        return self.__hourly_rate * self.__hours_worked

    # -- deadline overdue ---------------
    def is_overdue(self):
        try:
            dl = datetime.strptime(self.__deadline, "%Y-%m-%d").date()
            return dl < datetime.today().date() and self.__status != "Completed"
        except:
            return False

    # ----- to dictionary ---------------
    def to_dict(self):
        return {
            "project_id":   self.__project_id,
            "title":        self.__title,
            "client_id":    self.__client_id,
            "deadline":     self.__deadline,
            "hourly_rate":  self.__hourly_rate,
            "hours_worked": self.__hours_worked,
            "status":       self.__status,
            "description":  self.__description
        }

    # ----- from dictionary to project object ---------
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["project_id"],
            data["title"],
            data["client_id"],
            data["deadline"],
            data["hourly_rate"],
            data["hours_worked"],
            data["status"],
            data.get("description", "")
        )

    # ----- string representation ---------------
    def __str__(self):
        overdue_tag = "  OVERDUE!" if self.is_overdue() else ""
        return (f"  ID          : {self.__project_id}\n"
                f"  Title       : {self.__title}\n"
                f"  Client ID   : {self.__client_id}\n"
                f"  Deadline    : {self.__deadline}{overdue_tag}\n"
                f"  Rate/hr     : ${self.__hourly_rate:.2f}\n"
                f"  Hours       : {self.__hours_worked}\n"
                f"  Earnings    : ${self.gross_earning():.2f}\n"
                f"  Status      : {self.__status}\n"
                f"  Description : {self.__description}")
