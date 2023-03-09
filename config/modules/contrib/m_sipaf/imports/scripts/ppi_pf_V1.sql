-- import V1
-- (sans les données spécificité, matériaux, et ouvrage_type)
select
    id_import,
    uuid_pf as code_passage_faune,
    CASE
        WHEN pi_ou_ps = 'PI' THEN FALSE
        WHEN pi_ou_ps = 'PS' THEN TRUE
        WHEN pi_ou_ps = '' THEN NULL
        ELSE NULL
    END AS pi_ou_ps,
    pr,
    pr_abs,
    st_asewkt(
        st_makepoint(
            replace(X, ',', '.') :: numeric,
            replace(y, ',', '.') :: numeric,
            4326
        )
    ) AS GEOM,
    ID_PF_GEST AS code_ouvrage_gestionnaire,
    NOM_PF AS nom_usuel_passage_faune,
    CASE
        WHEN ISSU_REQA = 'oui' THEN TRUE
        ELSE NULL
    END AS issu_requalification,
    replace(larg_ouvra, ',', '.') :: numeric AS largeur_ouvrage,
    replace(haut_ouvra, ',', '.') :: NUMERIC AS hauteur_ouvrage,
    replace(long_franc, ',', '.') :: NUMERIC AS longueur_franchissement,
    replace(diam, ',', '.') :: NUMERIC AS diametre,
    replace(larg_disp, ',', '.') :: NUMERIC AS largeur_dispo_faune,
    replace(haut_disp, ',', '.') :: NUMERIC AS hauteur_dispo_faune,
    source
ORDER BY
    tis.uuid_pf;