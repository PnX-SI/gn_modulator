DROP VIEW IF EXISTS import_sinp_sipaf.v_sinp;

CREATE VIEW import_sinp_sipaf.v_sinp AS WITH geom AS (
    SELECT
        geom,
        cleobjet AS cleobjet,
        x_prec
    FROM
        import_sinp_sipaf.point
    UNION
    SELECT
        geom,
        cleobjet AS cleobjet,
        x_prec
    FROM
        import_sinp_sipaf.ligne
    UNION
    SELECT
        geom,
        cleobjet AS cleobjet,
        x_prec
    FROM
        import_sinp_sipaf.polygone
),
num AS (
    SELECT
    p.cleobs,
    CASE WHEN altmax is NULL THEN NULL ELSE ROUND(altmax::NUMERIC) END AS altmax,
    CASE WHEN altmin is NULL THEN NULL ELSE ROUND(altmin::NUMERIC) END AS altmin,
    CASE WHEN altmoy is NULL THEN NULL ELSE ROUND(altmoy::NUMERIC) END AS altmoy,
    CASE WHEN profmax is NULL THEN NULL ELSE ROUND(profmax::NUMERIC) END AS profmax,
    CASE WHEN profmin is NULL THEN NULL ELSE ROUND(profmin::NUMERIC) END AS profmin,
    CASE WHEN profmoy is NULL THEN NULL ELSE ROUND(profmoy::NUMERIC) END AS profmoy,
    CASE WHEN denbrmax is NULL THEN NULL ELSE ROUND(denbrmax::NUMERIC) END AS denbrmax,
    CASE WHEN denbrmin is NULL THEN NULL ELSE ROUND(denbrmin::NUMERIC) END AS denbrmin
    FROM import_sinp_sipaf.st_principal p
)
SELECT
    COALESCE(n.altmax, n.altmoy) AS altmax,
    COALESCE(n.altmin, n.altmoy) AS altmin,
    cdnom,
    "comment",
    n.denbrmax,
    n.denbrmin,
    datefin,
    datedebut,
    COALESCE(n.profmax, n.profmoy) AS profmax,
    COALESCE(n.profmin, n.profmoy) AS profmin,
    detminer,
    --p.idorigine,
    methgrp,
    occomporte,
    ocetatbio,
    ocbiogeo,
    ocstatbio,
    ocmethdet,
    typgrp,
    ocstade,
    ocnat,
    objdenbr,
    statobs,
    obstech,
    sensiniveau,
    ocsexe,
    statsource,
    nomcite,
    preuvnonum,
    nomlieu,
    identobs,
    x_prec,
    refbiblio,
    idsinpocc,
    idsinpgrp,
    ST_ASTEXT(geom) as "geometry",
    p.cleobs,
    -- datedet,
    -- dspublique,
    --effech,
    idjdd,
    -- obsctx,
    obsdescr -- orggestdat,
    -- sensiniveauvalue,
    -- taiech,
    -- techech,
    -- urpreuvnum,
    -- uttaiech,
FROM
    import_sinp_sipaf.st_principal p
    JOIN geom g ON g.cleobjet = p.cleobjet
    JOIN num n ON n.cleobs = p.cleobs
    LEFT JOIN import_sinp_sipaf.st_descr d ON d.cleobs = p.cleobs
    LEFT JOIN import_sinp_sipaf.st_regrp r ON r.clegrp = substring(p.clegrp, 0, strpos(p.clegrp, '.'))
    ;