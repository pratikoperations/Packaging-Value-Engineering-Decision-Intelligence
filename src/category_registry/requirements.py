from __future__ import annotations

from .models import DocumentDefinition as D, FieldDefinition as F, TestDefinition as T

M, R, O = "mandatory", "recommended", "optional"

COMMON_ANALYSES = (
    "cost_comparison", "annual_gross_saving", "expected_realized_saving",
    "first_year_net_benefit", "payback_period", "material_reduction",
    "document_completeness", "testing_checklist",
)
COMMON_UNAVAILABLE = ("final_technical_feasibility", "engineering_approval", "autonomous_approval")
COMMON_DOCUMENTS = (
    D("current_specification", M, True), D("proposed_specification", M, True),
    D("supplier_quotation", M), D("drawing", R), D("laboratory_report", R),
    D("trial_report", R), D("regulatory_certificate", R),
    D("sustainability_certificate", O), D("damage_history", O),
)

CATEGORY_REQUIREMENTS = {
"corrugated": {
 "fields": (
    F("length_mm","Legacy length",M,"number",("mm",),1,description="Retained for backward compatibility; internal/external dimensions provide the PVE 1.2 detail."),
    F("width_mm","Legacy width",M,"number",("mm",),1,description="Retained for backward compatibility; internal/external dimensions provide the PVE 1.2 detail."),
    F("height_mm","Legacy height",M,"number",("mm",),1,description="Retained for backward compatibility; internal/external dimensions provide the PVE 1.2 detail."),
    F("box_style","Box style",M,"text",description="Use a configured box-style value or a documented other style."),
    F("converting_profile","Converting profile",M,"text",description="Configured converting process; does not imply machine compatibility."),
    F("internal_length_mm","Internal length",M,"number",("mm",),1),
    F("internal_width_mm","Internal width",M,"number",("mm",),1),
    F("internal_height_mm","Internal height",M,"number",("mm",),1),
    F("external_length_mm","External length",R,"number",("mm",),1),
    F("external_width_mm","External width",R,"number",("mm",),1),
    F("external_height_mm","External height",R,"number",("mm",),1),
    F("ply","Ply",M,"integer",("ply",),1,9),
    F("flute_combination","Flute combination",M,"text"),
    F("flute","Legacy flute",O,"text",description="Retained for backward compatibility; prefer flute_combination."),
    F("paper_layer_structure","Paper-layer structure",M,"text",description="Ordered liner and medium structure."),
    F("layer_gsm_profile","Layer GSM profile",M,"text",description="Ordered layer GSM values with traceable specification reference."),
    F("layer_gsm","Legacy layer-wise GSM",O,"number",("gsm",),1,description="Retained for backward compatibility."),
    F("board_grade","Board grade",M,"text"),
    F("board_caliper_mm","Board caliper",R,"number",("mm",),0),
    F("joint_type","Joint type",M,"text"),
    F("closure_method","Closure method",M,"text"),
    F("print_process","Print process",R,"text"),
    F("print_colour_count","Print colour count",R,"integer",("count",),0,8),
    F("coating_or_treatment","Coating or treatment",R,"text"),
    F("blank_length_mm","Blank length",O,"number",("mm",),1),
    F("blank_width_mm","Blank width",O,"number",("mm",),1),
    F("manufacturers_joint_mm","Manufacturer joint",O,"number",("mm",),0),
    F("gross_packed_weight_kg","Gross packed weight",M,"number",("kg",),0),
    F("case_pack_quantity","Case pack quantity",M,"integer",("units/case",),1),
    F("artwork_revision","Artwork revision",R,"text"),
    F("barcode_or_qr_location","Barcode or QR location",R,"text"),
    F("transport_markings","Transport markings",R,"text"),
    F("regulatory_markings","Regulatory markings",R,"text",critical=True),
    F("dangerous_goods_marking_applicable","Dangerous-goods marking applicable",R,"boolean"),
    F("customer_artwork_approval_required","Customer artwork approval required",R,"boolean"),
    F("printing_plate_change_required","Printing plate or stereo change required",O,"boolean"),
    F("stack_height","Stack height",R,"number",("layers","m"),0),
    F("storage_duration_days","Storage duration",R,"number",("days",),0),
    F("humidity_percent","Humidity",R,"number",("%RH",),0,100),
    F("ect_kn_m","ECT",R,"number",("kN/m",),0),
    F("bct_n","BCT",R,"number",("N",),0,critical=True),
    F("burst_kpa","Bursting strength",R,"number",("kPa",),0),
 ),
 "tests": (T("GSM"),T("Moisture"),T("ECT"),T("BCT",True),T("Burst"),T("Drop"),T("Vibration"),T("Stacking"),T("Route trial")),
 "blockers": ("missing_baseline_specification","missing_proposed_specification","missing_critical_compression_test","category_mismatch"),
 "warnings": (
    "Supplier-declared ECT/BCT/burst values are not laboratory-tested values.",
    "Configured box style and converting profile do not establish packing-line compatibility.",
    "Tolerance limits must be sourced, versioned and explicitly validated.",
 ),
},
"folding_carton": {
 "fields": (F("length_mm","Length",M,"number",("mm",),1),F("width_mm","Width",M,"number",("mm",),1),F("height_mm","Height",M,"number",("mm",),1),F("board_gsm","Board GSM",M,"number",("gsm",),1),F("caliper_microns","Caliper",R,"number",("micron",),0),F("stiffness","Stiffness",R,"number",("mN","Taber"),0),F("crease_performance","Crease performance",R,"text"),F("print_method","Print method",M,"text"),F("coating","Coating",R,"text"),F("product_weight_g","Product weight",M,"number",("g",),0),F("compression_requirement_n","Compression requirement",R,"number",("N",),0,critical=True)),
 "tests": (T("GSM"),T("Caliper"),T("Stiffness"),T("Crease"),T("Compression",True),T("Rub resistance"),T("Print quality"),T("Packing-line trial")),
 "blockers": ("missing_baseline_specification","missing_proposed_specification","missing_critical_compression_requirement"),
 "warnings": ("Structural and print performance require converter and line validation.",),
},
"rigid_plastic": {
 "fields": (F("container_weight_g","Container weight",M,"number",("g",),0),F("resin_grade","Resin grade",M,"text"),F("wall_thickness_mm","Wall thickness",R,"number",("mm",),0),F("capacity_ml","Capacity",M,"number",("ml","L"),0),F("top_load_n","Top load",R,"number",("N",),0,critical=True),F("drop_performance","Drop performance",R,"text"),F("leak_test","Leak test",R,"text",critical=True),F("torque_requirement_nm","Torque requirement",R,"number",("N.m",),0),F("pcr_percent","PCR percentage",R,"number",("%",),0,100),F("mould_reference","Mould reference",M,"text")),
 "tests": (T("Weight"),T("Capacity"),T("Top load",True),T("Drop"),T("Leak",True),T("Torque"),T("Dimensional inspection"),T("Product compatibility",True)),
 "blockers": ("missing_resin_grade","missing_mould_reference","missing_leak_or_compatibility_evidence"),
 "warnings": ("Resin, mould and product-contact compatibility require engineering validation.",),
},
"flexible_packaging": {
 "fields": (F("laminate_structure","Laminate structure",M,"text"),F("total_thickness_microns","Total thickness",M,"number",("micron",),0),F("layer_thicknesses","Layer thicknesses",R,"text"),F("otr","OTR",R,"number",("cc/m2/day",),0,critical=True),F("wvtr","WVTR",R,"number",("g/m2/day",),0,critical=True),F("seal_strength_n_15mm","Seal strength",R,"number",("N/15mm",),0),F("bond_strength_n_15mm","Bond strength",R,"number",("N/15mm",),0),F("cof","COF",R,"number",("unitless",),0),F("puncture_resistance_n","Puncture resistance",R,"number",("N",),0),F("migration_compliance","Migration compliance",M,"text",critical=True)),
 "tests": (T("Thickness"),T("OTR",True),T("WVTR",True),T("Seal strength"),T("Bond strength"),T("COF"),T("Migration",True),T("Pouch burst or drop"),T("Shelf-life validation",True)),
 "blockers": ("missing_laminate_structure","missing_migration_compliance","missing_required_barrier_evidence"),
 "warnings": ("Barrier and shelf-life suitability cannot be concluded without product-specific validation.",),
},
"labels": {
 "fields": (F("substrate","Substrate",M,"text"),F("adhesive","Adhesive",M,"text"),F("label_length_mm","Label length",M,"number",("mm",),0),F("label_width_mm","Label width",M,"number",("mm",),0),F("peel_strength_n","Peel strength",R,"number",("N",),0),F("tack","Tack",R,"number",("N","loop_tack"),0),F("temperature_min_c","Minimum temperature",R,"number",("C",)),F("temperature_max_c","Maximum temperature",R,"number",("C",)),F("print_durability","Print durability",R,"text"),F("application_speed_per_min","Application speed",R,"number",("labels/min",),0),F("migration_requirement","Migration requirement",M,"text",critical=True)),
 "tests": (T("Adhesion"),T("Peel"),T("Tack"),T("Temperature resistance"),T("Print durability"),T("Application-line trial",True),T("Migration",True)),
 "blockers": ("missing_substrate_or_adhesive","missing_application_conditions","missing_migration_evidence_when_applicable"),
 "warnings": ("Adhesive performance depends on substrate, surface, temperature and application line.",),
},
"closures": {
 "fields": (F("closure_dimensions","Closure dimensions",M,"text"),F("resin","Resin",M,"text"),F("weight_g","Weight",M,"number",("g",),0),F("torque_nm","Torque",R,"number",("N.m",),0,critical=True),F("leakage","Leakage",R,"text",critical=True),F("liner_type","Liner type",R,"text"),F("thread_compatibility","Thread compatibility",M,"text",critical=True),F("tamper_evidence","Tamper evidence",R,"text"),F("opening_force_n","Opening force",R,"number",("N",),0)),
 "tests": (T("Torque",True),T("Leakage",True),T("Opening force"),T("Thread fit",True),T("Tamper evidence"),T("Drop"),T("Product compatibility",True)),
 "blockers": ("missing_thread_compatibility","missing_leakage_test","missing_product_compatibility"),
 "warnings": ("Closure and container interfaces must be validated as a system.",),
},
"glass": {
 "fields": (F("capacity_ml","Capacity",M,"number",("ml","L"),0),F("weight_g","Weight",M,"number",("g",),0),F("dimensions","Dimensions",M,"text"),F("wall_distribution","Wall distribution",R,"text"),F("impact_resistance","Impact resistance",R,"number",("J",),0),F("pressure_resistance_bar","Pressure resistance",R,"number",("bar",),0,critical=True),F("thermal_shock_c","Thermal shock",R,"number",("C",),0,critical=True),F("dimensional_tolerance","Dimensional tolerance",R,"text"),F("product_compatibility","Product compatibility",M,"text",critical=True)),
 "tests": (T("Impact"),T("Pressure",True),T("Thermal shock",True),T("Dimensional tolerance"),T("Capacity"),T("Product compatibility",True),T("Transport trial")),
 "blockers": ("missing_product_compatibility","missing_pressure_or_thermal_shock_evidence_when_applicable"),
 "warnings": ("Glass lightweighting requires container-specific structural and line validation.",),
},
"metal": {
 "fields": (F("gauge_mm","Gauge",M,"number",("mm",),0),F("metal_type","Alloy or metal type",M,"text"),F("coating","Coating",M,"text"),F("seam_specification","Seam specification",R,"text",critical=True),F("burst_pressure_bar","Burst pressure",R,"number",("bar",),0,critical=True),F("corrosion_resistance","Corrosion resistance",R,"text"),F("migration_compliance","Migration compliance",M,"text",critical=True),F("product_compatibility","Product compatibility",M,"text",critical=True)),
 "tests": (T("Gauge"),T("Seam integrity",True),T("Burst pressure",True),T("Corrosion"),T("Coating integrity"),T("Migration",True),T("Transport trial")),
 "blockers": ("missing_metal_or_coating_specification","missing_seam_integrity_evidence","missing_migration_or_product_compatibility"),
 "warnings": ("Coating, seam and product compatibility require category engineering approval.",),
},
}

for value in CATEGORY_REQUIREMENTS.values():
    value["documents"] = COMMON_DOCUMENTS
    value["available_analyses"] = COMMON_ANALYSES
    value["unavailable_analyses"] = COMMON_UNAVAILABLE
