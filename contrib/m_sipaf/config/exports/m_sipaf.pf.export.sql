WITH pre AS
  (SELECT
     (SELECT concat(utilisateurs.bib_organismes.nom_organisme, '/', ref_nomenclatures.t_nomenclatures.label_fr) AS concat_1
      FROM utilisateurs.bib_organismes,
           ref_nomenclatures.t_nomenclatures
      WHERE utilisateurs.bib_organismes.id_organisme = actors.id_organism
        AND ref_nomenclatures.t_nomenclatures.id_nomenclature = actors.id_nomenclature_type_actor) AS "actors.label_acteur",
          pr_sipaf.t_passages_faune.code_ouvrage_gestionnaire AS code_ouvrage_gestionnaire,
          pr_sipaf.t_passages_faune.date_creation_ouvrage AS date_creation_ouvrage,
          pr_sipaf.t_passages_faune.date_requalification_ouvrage AS date_requalification_ouvrage,
          pr_sipaf.t_passages_faune.diametre AS diametre,
          ST_AsText(pr_sipaf.t_passages_faune.geom) AS geom_text,
          ST_X(ST_Centroid(pr_sipaf.t_passages_faune.geom)) AS geom_x,
          ST_Y(ST_Centroid(pr_sipaf.t_passages_faune.geom)) AS geom_y,
          pr_sipaf.t_passages_faune.hauteur_dispo_faune AS hauteur_dispo_faune,
          pr_sipaf.t_passages_faune.id_passage_faune AS id_passage_faune,

     (SELECT string_agg(ref_geo.l_areas.area_name, ', ') AS string_agg_2
      FROM ref_geo.l_areas,
           pr_sipaf.cor_area_pf,
           ref_geo.bib_areas_types
      WHERE pr_sipaf.cor_area_pf.id_passage_faune = pr_sipaf.t_passages_faune.id_passage_faune
        AND pr_sipaf.cor_area_pf.id_area = ref_geo.l_areas.id_area
        AND ref_geo.bib_areas_types.id_type = ref_geo.l_areas.id_type
        AND ref_geo.bib_areas_types.type_code = 'COM') AS label_communes,

     (SELECT string_agg(ref_geo.l_areas.area_name, ', ') AS string_agg_3
      FROM ref_geo.l_areas,
           pr_sipaf.cor_area_pf,
           ref_geo.bib_areas_types
      WHERE pr_sipaf.cor_area_pf.id_passage_faune = pr_sipaf.t_passages_faune.id_passage_faune
        AND pr_sipaf.cor_area_pf.id_area = ref_geo.l_areas.id_area
        AND ref_geo.bib_areas_types.id_type = ref_geo.l_areas.id_type
        AND ref_geo.bib_areas_types.type_code = 'DEP') AS label_departements,

     (SELECT string_agg(ref_geo.l_linears.linear_name, ', ') AS string_agg_1
      FROM ref_geo.l_linears,
           pr_sipaf.cor_linear_pf
      WHERE pr_sipaf.cor_linear_pf.id_passage_faune = pr_sipaf.t_passages_faune.id_passage_faune
        AND pr_sipaf.cor_linear_pf.id_linear = ref_geo.l_linears.id_linear) AS label_infrastructures,

     (SELECT string_agg(ref_geo.l_areas.area_name, ', ') AS string_agg_4
      FROM ref_geo.l_areas,
           pr_sipaf.cor_area_pf,
           ref_geo.bib_areas_types
      WHERE pr_sipaf.cor_area_pf.id_passage_faune = pr_sipaf.t_passages_faune.id_passage_faune
        AND pr_sipaf.cor_area_pf.id_area = ref_geo.l_areas.id_area
        AND ref_geo.bib_areas_types.id_type = ref_geo.l_areas.id_type
        AND ref_geo.bib_areas_types.type_code = 'REG') AS label_regions,
          pr_sipaf.t_passages_faune.largeur_dispo_faune AS largeur_dispo_faune,
          pr_sipaf.t_passages_faune.largeur_ouvrage AS largeur_ouvrage,
          pr_sipaf.t_passages_faune.longueur_franchissement AS longueur_franchissement,
          pr_sipaf.t_passages_faune.nom_usuel_passage_faune AS nom_usuel_passage_faune,
          nomenclature_ouvrage_hydrau_banq_caract.label_fr AS "nomenclature_ouvrage_hydrau_banq_caract.label_fr",
          nomenclature_ouvrage_hydrau_banq_type.label_fr AS "nomenclature_ouvrage_hydrau_banq_type.label_fr",
          nomenclature_ouvrage_hydrau_position.label_fr AS "nomenclature_ouvrage_hydrau_position.label_fr",
          nomenclature_ouvrage_specificite.label_fr AS "nomenclature_ouvrage_specificite.label_fr",
          nomenclatures_ouvrage_categorie.label_fr AS "nomenclatures_ouvrage_categorie.label_fr",
          nomenclatures_ouvrage_materiaux.label_fr AS "nomenclatures_ouvrage_materiaux.label_fr",
          nomenclatures_ouvrage_type.label_fr AS "nomenclatures_ouvrage_type.label_fr",
          pr_sipaf.t_passages_faune.ouvrag_hydrau_tirant_air AS ouvrag_hydrau_tirant_air,
          pr_sipaf.t_passages_faune.ouvrage_hydrau AS ouvrage_hydrau,
          pr_sipaf.t_passages_faune.pi_ou_ps AS pi_ou_ps,
          pr_sipaf.t_passages_faune.source AS source,
          "usages.nomenclature_usage_type".label_fr AS "usages.nomenclature_usage_type.label_fr",
          pr_sipaf.t_passages_faune.uuid_passage_faune AS uuid_passage_faune
   FROM pr_sipaf.t_passages_faune
   LEFT OUTER JOIN (pr_sipaf.cor_pf_nomenclature_ouvrage_type AS cor_pf_nomenclature_ouvrage_type_1
                    JOIN ref_nomenclatures.t_nomenclatures AS nomenclatures_ouvrage_type ON nomenclatures_ouvrage_type.id_nomenclature = cor_pf_nomenclature_ouvrage_type_1.id_nomenclature) ON pr_sipaf.t_passages_faune.id_passage_faune = cor_pf_nomenclature_ouvrage_type_1.id_passage_faune
   LEFT OUTER JOIN (pr_sipaf.cor_pf_nomenclature_ouvrage_materiaux AS cor_pf_nomenclature_ouvrage_materiaux_1
                    JOIN ref_nomenclatures.t_nomenclatures AS nomenclatures_ouvrage_materiaux ON nomenclatures_ouvrage_materiaux.id_nomenclature = cor_pf_nomenclature_ouvrage_materiaux_1.id_nomenclature) ON pr_sipaf.t_passages_faune.id_passage_faune = cor_pf_nomenclature_ouvrage_materiaux_1.id_passage_faune
   LEFT OUTER JOIN ref_nomenclatures.t_nomenclatures AS nomenclature_ouvrage_specificite ON nomenclature_ouvrage_specificite.id_nomenclature = pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_specificite
   LEFT OUTER JOIN (pr_sipaf.cor_pf_nomenclature_ouvrage_categorie AS cor_pf_nomenclature_ouvrage_categorie_1
                    JOIN ref_nomenclatures.t_nomenclatures AS nomenclatures_ouvrage_categorie ON nomenclatures_ouvrage_categorie.id_nomenclature = cor_pf_nomenclature_ouvrage_categorie_1.id_nomenclature) ON pr_sipaf.t_passages_faune.id_passage_faune = cor_pf_nomenclature_ouvrage_categorie_1.id_passage_faune
   LEFT OUTER JOIN ref_nomenclatures.t_nomenclatures AS nomenclature_ouvrage_hydrau_position ON nomenclature_ouvrage_hydrau_position.id_nomenclature = pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_hydrau_position
   LEFT OUTER JOIN ref_nomenclatures.t_nomenclatures AS nomenclature_ouvrage_hydrau_banq_caract ON nomenclature_ouvrage_hydrau_banq_caract.id_nomenclature = pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_hydrau_banq_caract
   LEFT OUTER JOIN ref_nomenclatures.t_nomenclatures AS nomenclature_ouvrage_hydrau_banq_type ON nomenclature_ouvrage_hydrau_banq_type.id_nomenclature = pr_sipaf.t_passages_faune.id_nomenclature_ouvrage_hydrau_banq_type
   LEFT OUTER JOIN pr_sipaf.cor_actor_pf AS actors ON pr_sipaf.t_passages_faune.id_passage_faune = actors.id_passage_faune
   LEFT OUTER JOIN pr_sipaf.t_usages AS usages ON pr_sipaf.t_passages_faune.id_passage_faune = usages.id_passage_faune
   LEFT OUTER JOIN ref_nomenclatures.t_nomenclatures AS "usages.nomenclature_usage_type" ON "usages.nomenclature_usage_type".id_nomenclature = usages.id_nomenclature_usage_type)
SELECT STRING_AGG(DISTINCT "actors.label_acteur", ', ') AS "Acteurs",
       code_ouvrage_gestionnaire AS "Code ouvrage gestionnaire",
       date_creation_ouvrage AS "Date de réalisation",
       date_requalification_ouvrage AS "Date de requalification",
       diametre AS "Diamètre (m)",
       geom_text AS "Geométrie (text)",
       geom_x AS "Longitude",
       geom_y AS "Latitude",
       hauteur_dispo_faune AS "Hauteur disponible (m)",
       id_passage_faune AS "ID",
       label_communes AS "Commune(s)",
       label_departements AS "Département(s)",
       label_infrastructures AS "Infrastructure traversée",
       label_regions AS "Région(s)",
       largeur_dispo_faune AS "Largeur disponible (m)",
       largeur_ouvrage AS "Largeur ouvrage (m)",
       longueur_franchissement AS "Longueur de franchissement (m)",
       nom_usuel_passage_faune AS "Nom Passage Faune",
       "nomenclature_ouvrage_hydrau_banq_caract.label_fr" AS "OH Caractérisation banquette",
       "nomenclature_ouvrage_hydrau_banq_type.label_fr" AS "OH type de banquette",
       "nomenclature_ouvrage_hydrau_position.label_fr" AS "Position banquette",
       "nomenclature_ouvrage_specificite.label_fr" AS "Spécificité du passage faune",
       STRING_AGG(DISTINCT "nomenclatures_ouvrage_categorie.label_fr", ', ') AS "Catégorie d'ouvrage",
       STRING_AGG(DISTINCT "nomenclatures_ouvrage_materiaux.label_fr", ', ') AS "Matériaux",
       STRING_AGG(DISTINCT "nomenclatures_ouvrage_type.label_fr", ', ') AS "Type d'ouvrage",
       ouvrag_hydrau_tirant_air AS "Tirant d'air banquette (m)",
       ouvrage_hydrau AS "Ouvrage hydraulique",
       pi_ou_ps AS "Positionnement",
       source AS "Source",
                 STRING_AGG(DISTINCT "usages.nomenclature_usage_type.label_fr", ', ') AS "Usages",
                 uuid_passage_faune AS "Identifiant UUID"
FROM pre
GROUP BY code_ouvrage_gestionnaire,
         date_creation_ouvrage,
         date_requalification_ouvrage,
         diametre,
         geom_text,
         geom_x,
         geom_y,
         hauteur_dispo_faune,
         id_passage_faune,
         label_communes,
         label_departements,
         label_infrastructures,
         label_regions,
         largeur_dispo_faune,
         largeur_ouvrage,
         longueur_franchissement,
         nom_usuel_passage_faune,
         "nomenclature_ouvrage_hydrau_banq_caract.label_fr",
         "nomenclature_ouvrage_hydrau_banq_type.label_fr",
         "nomenclature_ouvrage_hydrau_position.label_fr",
         "nomenclature_ouvrage_specificite.label_fr",
         ouvrag_hydrau_tirant_air,
         ouvrage_hydrau,
         pi_ou_ps,
         source,
         uuid_passage_faune