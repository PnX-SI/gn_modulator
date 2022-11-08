import pytest  # noqa
from gn_modules.schema import SchemaMethods


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestGrammar:
    """Test unitaire sur les fonction de grammaire"""

    def test_grammar_m(self):
        """Masculin"""

        sm = SchemaMethods("commons.module")
        assert sm.label() == "module"
        assert sm.labels() == "modules"
        assert sm.le_label() == "le module"
        assert sm.les_labels() == "les modules"
        assert sm.un_label() == "un module"
        assert sm.des_labels() == "des modules"
        assert sm.un_nouveau_label() == "un nouveau module"
        assert sm.du_nouveau_label() == "du nouveau module"
        assert sm.d_un_nouveau_label() == "d'un nouveau module"
        assert sm.des_nouveaux_labels() == "des nouveaux modules"
        assert sm.du_label() == "du module"

    def test_grammar_f(self):
        """Féminin"""

        sm = SchemaMethods("ref_geo.area")
        assert sm.label() == "géométrie"
        assert sm.labels() == "géométries"
        assert sm.le_label() == "la géométrie"
        assert sm.les_labels() == "les géométries"
        assert sm.un_label() == "une géométrie"
        assert sm.des_labels() == "des géométries"
        assert sm.un_nouveau_label() == "une nouvelle géométrie"
        assert sm.du_nouveau_label() == "de la nouvelle géométrie"
        assert sm.d_un_nouveau_label() == "d'une nouvelle géométrie"
        assert sm.des_nouveaux_labels() == "des nouvelles géométries"
        assert sm.du_label() == "de la géométrie"

    def test_grammar_m_v(self):
        """Masculin voyelle 1ère lettre"""

        sm = SchemaMethods("user.role")
        assert sm.label() == "utilisateur"
        assert sm.labels() == "utilisateurs"
        assert sm.le_label() == "l'utilisateur"
        assert sm.les_labels() == "les utilisateurs"
        assert sm.un_label() == "un utilisateur"
        assert sm.des_labels() == "des utilisateurs"
        assert sm.un_nouveau_label() == "un nouvel utilisateur"
        assert sm.du_nouveau_label() == "du nouvel utilisateur"
        assert sm.d_un_nouveau_label() == "d'un nouvel utilisateur"
        assert sm.des_nouveaux_labels() == "des nouveaux utilisateurs"
        assert sm.du_label() == "de l'utilisateur"

    def test_grammar_f_v(self):
        """Féminin voyelle 1ère lettre"""

        sm = SchemaMethods("m_monitoring.observation")
        assert sm.label() == "observation"
        assert sm.labels() == "observations"
        assert sm.le_label() == "l'observation"
        assert sm.les_labels() == "les observations"
        assert sm.un_label() == "une observation"
        assert sm.des_labels() == "des observations"
        assert sm.un_nouveau_label() == "une nouvelle observation"
        assert sm.du_nouveau_label() == "de la nouvelle observation"
        assert sm.d_un_nouveau_label() == "d'une nouvelle observation"
        assert sm.des_nouveaux_labels() == "des nouvelles observations"
        assert sm.du_label() == "de l'observation"

    def test_grammar_labels(self):
        """labels
        quand il y a un besoin de définir le pluriel
        par défaut on rajoute un s à la fin de 'label'
        """

        sm = SchemaMethods("meta.jdd")
        assert sm.label() == "jeu de données"
        assert sm.labels() == "jeux de données"
        assert sm.le_label() == "le jeu de données"
        assert sm.les_labels() == "les jeux de données"
        assert sm.un_label() == "un jeu de données"
        assert sm.des_labels() == "des jeux de données"
        assert sm.un_nouveau_label() == "un nouveau jeu de données"
        assert sm.du_nouveau_label() == "du nouveau jeu de données"
        assert sm.d_un_nouveau_label() == "d'un nouveau jeu de données"
        assert sm.des_nouveaux_labels() == "des nouveaux jeux de données"
        assert sm.du_label() == "du jeu de données"

    def test_grammar_redefinition(self):
        """Quand on choisi de redéfinir le label (et/ou labels, genre)
        pour un contexte particulier
        """

        sm = SchemaMethods("m_monitoring.site")
        redefinition = {"label": "éolienne", "genre": "F"}
        assert sm.label(redefinition) == "éolienne"
        assert sm.labels(redefinition) == "éoliennes"
        assert sm.le_label(redefinition) == "l'éolienne"
        assert sm.les_labels(redefinition) == "les éoliennes"
        assert sm.un_label(redefinition) == "une éolienne"
        assert sm.des_labels(redefinition) == "des éoliennes"
        assert sm.un_nouveau_label(redefinition) == "une nouvelle éolienne"
        assert sm.du_nouveau_label(redefinition) == "de la nouvelle éolienne"
        assert sm.d_un_nouveau_label(redefinition) == "d'une nouvelle éolienne"
        assert sm.des_nouveaux_labels(redefinition) == "des nouvelles éoliennes"
        assert sm.du_label(redefinition) == "de l'éolienne"
