class UrlHandler():

    def __init__(
            self,
            link: str,
            appearances: int = 0,
            *args,
            **kwargs,
            ) -> None:

        self.link = link
        self.appearances = appearances

    def get_len(self):
        return len(self.link)

    def count_vowels(self):
        return len([l for l in self.link.lower() if l in ('a','e','i','o','u')])

    def count_consonants(self):
        return len([l for l in self.link.lower() if l not in ('a','e','i','o','u')])

    def count_lower(self):
        return len([l for l in self.link if l==l.lower()])

    def count_upper(self):
        return len([l for l in self.link if l==l.upper()])

    def get_vowels_vs_consonants(self):
        return self.count_vowels() * self.count_consonants()

    def get_lower_vs_upper(self):
        return self.count_lower() * self.count_upper()

    def get_type_vs_size(self):
        return self.get_vowels_vs_consonants() * self.get_lower_vs_upper()

    def count_vowels_proportion(self):
        return self.count_vowels() / self.get_len()

    def count_consonants_proportion(self):
        return self.count_consonants() / self.get_len()

    def generate_data(self):
        return {
            "link":self.link,
            "f1":self.get_len(),
            "f2":self.count_vowels(),
            "f3":self.count_consonants(),
            "f4":self.count_lower(),
            "f5":self.count_upper(),
            "f6":self.get_vowels_vs_consonants(),
            "f7":self.get_lower_vs_upper(),
            "f8":self.get_type_vs_size(),
            "f9":self.count_vowels_proportion(),
            "f10":self.count_consonants_proportion(),
            "appearances":self.appearances
        }

    