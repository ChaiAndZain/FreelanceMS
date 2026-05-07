class Client:
    """
    Client class
    """

    # ------- constructor -----------------
    def __init__(self, client_id, name, email, phone, company, payment_terms):
        # private attributes
        self.__client_id    = client_id      # unique ID (C001, C002..)
        self.__name      = name            # client name
        self.__email     = email          # contact email
        self.__phone     = phone           # phone number
        self.__company   = company         # company or organization
        self.__payment_terms = payment_terms # payment terms "Net 30", "Immediate"

    #  ------ getters -------------
    def get_id(self):           return self.__client_id
    def get_name(self):          return self.__name
    def get_email(self):        return self.__email
    def get_phone(self):        return self.__phone
    def get_company(self):       return self.__company
    def get_payment_terms(self): return self.__payment_terms

    # ----- etters ---------
    def set_name(self, name):            self.__name = name
    def set_email(self, email):          self.__email = email
    def set_phone(self, phone):           self.__phone = phone
    def set_company(self, company):       self.__company = company
    def set_payment_terms(self, terms):  self.__payment_terms = terms

    # ----- to dictionary ---------------
    def to_dict(self):
        return {
            "client_id":     self.__client_id,
            "name":          self.__name,
            "email":         self.__email,
            "phone":         self.__phone,
            "company":       self.__company,
            "payment_terms": self.__payment_terms
        }
    # ----- from dictionary to client object ---------
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["client_id"],
            data["name"],
            data["email"],
            data["phone"],
            data["company"],
            data["payment_terms"]
        )

    # ----- print overload -------
    def __str__(self):
        return (f"  ID       : {self.__client_id}\n"
                f"  Naam     : {self.__name}\n"
                f"  Email    : {self.__email}\n"
                f"  Phone    : {self.__phone}\n"
                f"  Company  : {self.__company}\n"
                f"  Payment  : {self.__payment_terms}")
