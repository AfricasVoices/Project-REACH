from core_data_modules.cleaners import somali


class ColumnSpecification(object):
    def __init__(self, source_field, auto_coded_field, manually_coded_field, coda_name, cleaner=None):
        self.source_field = source_field
        self.auto_coded_field = auto_coded_field
        self.manually_coded_field = manually_coded_field
        self.coda_name = coda_name
        self.cleaner = cleaner


class DatasetSpecification(object):
    columns = [
        ColumnSpecification("gender_review", "gender_clean", "gender_coded", "Gender",
                            somali.DemographicCleaner.clean_gender),
        ColumnSpecification("district_review", "district_clean", "district_coded", "District",
                            somali.DemographicCleaner.clean_somalia_district),
        ColumnSpecification("urban_rural_review", "urban_rural_clean", "urban_rural_coded", "Urban_Rural",
                            somali.DemographicCleaner.clean_urban_rural),
        ColumnSpecification("age_review", "age_clean", "age_coded", "Age",
                            somali.DemographicCleaner.clean_age),
        ColumnSpecification("assessment_review", "assessment_clean", "assessment_coded", "Assessment",
                            somali.DemographicCleaner.clean_yes_no),
        ColumnSpecification("idp_review", "idp_clean", "idp_coded", "IDP",
                            somali.DemographicCleaner.clean_yes_no),

        ColumnSpecification("involved_esc4jmcna", "involved_esc4jmcna_clean", "involved_esc4jmcna_coded", "Involved",
                            somali.DemographicCleaner.clean_yes_no),
        ColumnSpecification("repeated_esc4jmcna", "repeated_esc4jmcna_clean", "repeated_esc4jmcna_coded", "Repeated",
                            somali.DemographicCleaner.clean_yes_no)
    ]
