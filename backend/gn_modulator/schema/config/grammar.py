"""
    methodes pour la grammaire
"""

from gn_modulator.utils.commons import unaccent


class SchemaConfigGrammar:
    @classmethod
    def grammar_type_list(cls):
        """
        Retourne la liste des types de grammaire
        (depuis le dictionnaire renvoyé par la méthode config_display)
        """
        grammar_type_list = list(cls("commons.module").config_display().keys())

        grammar_type_list.remove("description")

        return grammar_type_list

    def config_display(self, object_definition={}):
        """
        frontend display (label, etc..)
        """
        return {
            "label": self.label(object_definition),
            "labels": self.labels(object_definition),
            "le_label": self.le_label(object_definition),
            "les_labels": self.les_labels(object_definition),
            "un_label": self.un_label(object_definition),
            "des_labels": self.des_labels(object_definition),
            "un_nouveau_label": self.un_nouveau_label(object_definition),
            "du_nouveau_label": self.du_nouveau_label(object_definition),
            "d_un_nouveau_label": self.d_un_nouveau_label(object_definition),
            "des_nouveaux_labels": self.des_nouveaux_labels(object_definition),
            "du_label": self.du_label(object_definition),
            "description": self.description(object_definition),
        }

    def genre(self, object_definition={}):
        """
        returns schema genre
        """

        return object_definition.get("genre") or self.attr("meta.genre")

    def new(self, object_definition={}):
        return (
            "nouvelle"
            if self.genre(object_definition) == "F"
            else (
                "nouvel"
                if self.is_first_letter_vowel(self.label(object_definition))
                else "nouveau"
            )
        )

    def news(self, object_definition={}):
        return "nouvelles" if self.genre(object_definition) == "F" else "nouveaux"

    def label(self, object_definition={}):
        """
        returns schema label in lowercase
        """
        label = object_definition.get("label") or self.attr("meta.label")
        return label.lower()

    def labels(self, object_definition={}):
        labels = (
            object_definition.get("labels")
            or self.attr("meta.labels")
            or f"{self.label(object_definition)}s"
        )

        return labels.lower()

    def is_first_letter_vowel(self, str):
        """
        returns True if unaccented first letter in 'aeiouy'
        """
        return unaccent(str[0]) in "aeiouy"

    def article_def(self, object_definition={}):
        """
        renvoie l'article défini pour le label

        prend en compte:
        - le genre (depuis $meta)
        - si le label commence par une voyelle
        - s'il y a un espace après l'article ou non
        """
        return (
            "l'"
            if self.is_first_letter_vowel(self.label(object_definition))
            else "la " if self.genre(object_definition) == "F" else "le "
        )

    def article_undef(self, object_definition={}):
        """
        renvoie l'article indéfini pour le label

        cf article_def
        """

        return "une " if self.genre(object_definition) == "F" else "un "

    def preposition(self, object_definition={}, check_voyel=True):
        """
        du, de la, de l'
        """
        return (
            "de l'"
            if self.is_first_letter_vowel(self.label(object_definition)) and check_voyel
            else "de la " if self.genre(object_definition) == "F" else "du "
        )

    def le_label(self, object_definition={}):
        """
        Renvoie le label précédé de l'article défini
        """
        return f"{self.article_def(object_definition)}{self.label(object_definition)}"

    def un_label(self, object_definition={}):
        """
        Renvoie le label précédé de l'article indéfini
        """
        return f"{self.article_undef(object_definition)}{self.label(object_definition)}"

    def un_nouveau_label(self, object_definition={}):
        """
        Renvoie le label précédé de l'article indéfini et de self.new()
        """
        return f"{self.article_undef(object_definition)}{self.new(object_definition)} {self.label(object_definition)}"

    def d_un_nouveau_label(self, object_definition={}):
        """
        Renvoie le label précédé de l'article indéfini et de self.new()
        """
        return f"d'{self.article_undef(object_definition)}{self.new(object_definition)} {self.label(object_definition)}"

    def du_nouveau_label(self, object_definition={}):
        """
        Renvoie le label précédé de la préposition et de self.new()
        """
        return f"{self.preposition(object_definition, check_voyel=False)}{self.new(object_definition)} {self.label(object_definition)}"

    def des_nouveaux_labels(self, object_definition={}):
        """
        Renvoie le labels précédé de l'article indéfini et de self.new()
        """
        return f"des {self.news(object_definition)} {self.labels(object_definition)}"

    def du_label(self, object_definition={}):
        """
        Renvoie le label précédé de la préposition
        """
        return f"{self.preposition(object_definition)}{self.label(object_definition)}"

    def les_labels(self, object_definition={}):
        return f"les {self.labels(object_definition)}"

    def des_labels(self, object_definition={}):
        return f"des {self.labels(object_definition)}"
