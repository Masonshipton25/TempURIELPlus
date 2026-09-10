import json
import logging
import math
import os
import re

import numpy as np
import pandas as pd

from .base_uriel import BaseURIEL


class URIELPlusDatabases(BaseURIEL):
    def _get_new_features(self, feats, columns):
        """
            Identifies and returns the new features to URIEL+.


            Args:
                feats (np.ndarray): The current features array.
                columns (list): The list of all features.


            Returns:
                list: A list of new features to URIEL+.
        """
        featlist = feats.tolist()
        return [feat for feat in columns if feat not in featlist]


    def _get_new_languages(self, langs, data, column):
        """
            Identifies and returns the new languages to URIEL+.


            Args:
                langs (np.ndarray): The current languages array.
                data (pd.DataFrame): The new dataset containing all languages.
                column (str): The column in the dataset that contains language codes.


            Returns:
                list: A list of new languages to URIEL+.
        """
        langlist = langs.tolist()
        return [lang for lang in data[column] if lang not in langlist]


    def _set_new_data_dimensions(self, data, new_feats, new_langs, new_sources):
        """
            Expands the URIEL+ data array to accommodate new features, languages, and sources, initializing new values
            to -1.0.


            Args:
                data (np.ndarray): The current data array.
                new_feats (list): List of new features to add.
                new_langs (list): List of new languages to add.
                new_sources (list): List of new sources to add.


            Returns:
                np.ndarray: The expanded data array with new dimensions.
        """
        new_data = np.full(
            (data.shape[0] + len(new_langs), data.shape[1] + len(new_feats), data.shape[2] + len(new_sources)),
            -1.0
        )
        new_data[:data.shape[0], :data.shape[1], :data.shape[2]] = data
        return new_data


    def is_database_incorporated(self, database):
        """
            Checks if a specific database has already been integrated into URIEL+.


            Args:
                database (str): The name of the database to check.
        """
        all_sources = [str(s).upper() for s in self.sources[1]]
        return database.upper() in all_sources


    def _calculate_phylogeny_vectors(self):
        """
            This function reads the relevant CSV file and updates the phylogeny arrays based on the full lineage
            of new languages. Each lineage node, from root to leaf, becomes its own path-qualified feature
            (F_<root> > <child> > ... > <node>), and every ancestor node in a language's lineage is set to 1.

            
            If caching is enabled, updates the "family_features.npz" file.
        """
        csv_path = os.path.join(self.cur_dir, "database", "urielplus_csvs", "lang_fam_geo.csv")
        fam_geo_feat_csv = pd.read_csv(csv_path)
        fam_geo_feat_csv.columns = fam_geo_feat_csv.columns.str.strip('"')

        new_langs = np.setdiff1d(self.langs[1], self.langs[0])

        # Work out each new language's lineage path (if any) and collect every brand-new path-qualified feature name across the whole batch, without touching any array yet.
        existing_feats = set(self.feats[0].tolist())
        lang_paths = [None] * len(new_langs)
        new_feature_order = []
        seen_new_features = set()

        for i, l in enumerate(new_langs):
            row = fam_geo_feat_csv.loc[fam_geo_feat_csv["language_id"] == l]
            if row.empty:
                continue

            lineage_value = row["lineage"].values[0]
            if not isinstance(lineage_value, str) or not lineage_value.strip():
                continue

            parts = [part.strip() for part in lineage_value.split(",") if part.strip()]
            if not parts:
                continue

            path_features = []
            path = []
            for part in parts:
                path.append(part)
                fam_string = "F_" + " > ".join(path)
                path_features.append(fam_string)
                if fam_string not in existing_feats and fam_string not in seen_new_features:
                    seen_new_features.add(fam_string)
                    new_feature_order.append(fam_string)

            lang_paths[i] = path_features

        # Batch-resize once, for every new language row and every new feature column together.
        self.data[0] = self._set_new_data_dimensions(self.data[0], new_feature_order, list(new_langs), [])
        self.feats[0] = np.append(self.feats[0], new_feature_order)
        self.langs[0] = np.append(self.langs[0], new_langs)

        feature_position = {str(feat): idx for idx, feat in enumerate(self.feats[0])}

        # Fill in values now that the array is already at its final shape. ---
        for i, path_features in enumerate(lang_paths):
            if path_features is None:
                continue  # no usable lineage; row stays at the default -1 (unknown) for every feature

            new_lang_idx = -len(new_langs) + i

            # Every existing family node is known to be absent for this language unless proven present below.
            self.data[0][new_lang_idx, :, -1] = 0.0

            for fam_string in path_features:
                family_idx = feature_position[fam_string]
                self.data[0][new_lang_idx, family_idx, -1] = 1.0

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[0]), feats=self.feats[0], data=self.data[0], langs=self.langs[0], sources=self.sources[0])

        self._sync_loaded_features(0)
        self._refresh_indexes(0)


    def _calculate_geocoord_vectors(self):
        """
            This function calculates geographic distance vectors between new languages and existing geocoordinates.
            Each new language gets a vector of distances to all known coordinates (in km), normalized by Earth's
            antipodal distance (π x 6371.0 km).
            Uses the provided getGreatCircleDistance function for great-circle distance.

            If caching is enabled, updates the `geocoord_features.npz` file.
        """
        new_langs = np.setdiff1d(self.langs[1], self.langs[2])
        self.langs[2] = np.append(self.langs[2], new_langs)
        self.data[2] = self._set_new_data_dimensions(self.data[2], [], new_langs, [])

        coords = [list(map(float, re.findall(r"-?\d+(?:\.\d+)?", feat))) for feat in self.feats[2]]

        csv_path = os.path.join(self.cur_dir, "database", "urielplus_csvs", "lang_fam_geo.csv")
        fam_geo_feat_csv = pd.read_csv(csv_path)
        fam_geo_feat_csv.columns = fam_geo_feat_csv.columns.str.strip('"')
        fam_geo_feat_csv["latitude"] = pd.to_numeric(fam_geo_feat_csv["latitude"], errors="coerce")
        fam_geo_feat_csv["longitude"] = pd.to_numeric(fam_geo_feat_csv["longitude"], errors="coerce")
        fam_geo_feat_csv["longitude"] = fam_geo_feat_csv["longitude"].apply(
            lambda x: x - 360 if x > 180 else (x + 360 if x < -180 else x)
        )
        fam_geo_feat_csv["latitude"] = fam_geo_feat_csv["latitude"].apply(lambda x: max(min(x, 90), -90))

        MAX_DIST = math.pi * 6371.000  # Earth's antipodal distance, ~20015.1 km

        # Function provided by Dr. Patrick Littell
        def getGreatCircleDistance(lat1, lon1, lat2, lon2):
            ''' Get the great-circle distance between two coordinates
                using the Haversine calculation '''

            f1 = math.radians(lat1)
            f2 = math.radians(lat2)
            df = math.radians(lat2-lat1)
            dl = math.radians(lon2-lon1)

            a = (math.sin(df/2) ** 2 +
                    math.cos(f1) * math.cos(f2) *
                    math.sin(dl/2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return 6371.000 * c

        for i, l in enumerate(new_langs):
            try:
                row = fam_geo_feat_csv.loc[fam_geo_feat_csv["language_id"].str.strip('"') == l]
                if row.empty:
                    self.data[2][-len(new_langs) + i, :, -1] = -1.0
                    continue

                lat, lon = row["latitude"].values[0], row["longitude"].values[0]
                if pd.isna(lat) or pd.isna(lon):
                    self.data[2][-len(new_langs) + i, :, -1] = -1.0
                    continue

                distances = []
                for c in coords:
                    if np.isnan(c[0]) or np.isnan(c[1]):
                        distances.append(-1.0)
                    else:
                        distances.append(getGreatCircleDistance(lat, lon, c[0], c[1]) / MAX_DIST)

                self.data[2][-len(new_langs) + i, :, -1] = np.array(distances, dtype=np.float32)

            except Exception:
                self.data[2][-len(new_langs) + i, :, -1] = -1.0

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[2]), feats=self.feats[2], data=self.data[2], langs=self.langs[2], sources=self.sources[2])

        self._sync_loaded_features(2)
        self._refresh_indexes(2)


    def _calculate_script_vectors(self):
        """
            This function calculates script vectors for new languages.

            If caching is enabled, updates the `script_features.npz` file.
        """
        csv_path = os.path.join(self.cur_dir, "database", "urielplus_csvs", "script_data.csv")
        script_csv = pd.read_csv(csv_path)
        script_csv.columns = script_csv.columns.str.strip('"')
        script_csv['language_id'] = script_csv['language_id'].str.strip('"')

        script_feat_cols = [col for col in script_csv.columns if col not in ['language_id', 'language_name']]

        missing_feats = [f for f in script_feat_cols if f not in self.feats[3]]
        if missing_feats:
            self.data[3] = self._set_new_data_dimensions(self.data[3], missing_feats, [], [])
            self.feats[3] = np.append(self.feats[3], missing_feats)

        new_langs = np.setdiff1d(self.langs[1], self.langs[3])
        self.langs[3] = np.append(self.langs[3], new_langs)
        self.data[3] = self._set_new_data_dimensions(self.data[3], [], new_langs, [])

        feat_position = {str(f): idx for idx, f in enumerate(self.feats[3])}

        for i, lang in enumerate(new_langs):
            lang_row = script_csv.loc[script_csv['language_id'] == lang]
            new_lang_idx = -len(new_langs) + i

            self.data[3][new_lang_idx, :, -1] = -1.0
            if not lang_row.empty:
                for col in script_feat_cols:
                    self.data[3][new_lang_idx, feat_position[col], -1] = float(lang_row[col].values[0])

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[3]), feats=self.feats[3], data=self.data[3], langs=self.langs[3], sources=self.sources[3])

        self._sync_loaded_features(3)
        self._refresh_indexes(3)


    def _get_or_create_derived_source(self):
        """
            Returns the index of the "DERIVED" pseudo-source in self.sources[1], creating an empty layer
            (initialized to -1 for every existing language and feature) if it does not already exist.
        """
        matches = np.where(self.sources[1] == "DERIVED")[0]
        if len(matches):
            return int(matches[0])
        self.data[1] = self._set_new_data_dimensions(self.data[1], [], [], ["DERIVED"])
        self.sources[1] = np.append(self.sources[1], "DERIVED")
        return len(self.sources[1]) - 1


    def _load_feature_mappings(self):
        """
            This function loads the JSON file defining feature consolidation mappings used for combining and
            inferring feature data in URIEL+.
        """
        path = os.path.join(self.cur_dir, "database", "urielplus_csvs", "feature_mappings.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


    def _ensure_feature_mappings(self):
        """
            This function ensures feature mappings are loaded before use.
        """
        if not hasattr(self, "feature_mappings"):
            self.feature_mappings = self._load_feature_mappings()


    def _feature_inclusion_map(self, database, columns):
        """
            Determines whether each raw column belonging to a database should become its own public
            typological feature, according to "feature_mappings.json".


            Args:
                database (str): The name of the database whose columns are being checked (e.g. "GRAMBANK").
                columns (list): The raw column names to check, exactly as they appear in the source CSV.


            Returns:
                dict: A mapping from each column name to True (disposition "represented", becomes its own
                feature) or False (disposition "collapsed_into" or "not_represented", excluded — either
                because it only feeds a separate exact_collapse target computed by inferred_features(), or
                because it maps to no public feature at all).


            Raises:
                ValueError: If a column is undocumented, a documented column is not present in columns, a
                column is documented more than once with conflicting dispositions, or a column is
                documented with a disposition other than "represented", "collapsed_into", or
                "not_represented".
        """
        self._ensure_feature_mappings()

        column_dispositions = {}
        for record in self.feature_mappings:
            if record.get("database") != database:
                continue

            # Ignore historical bundled conversion column mappings.
            if any(
                source_feature.get("namespace") in (
                    "urielplus_v1_bundled_conversion_column",
                    "removed_urielplus_operand",
                )
                for source_feature in record.get("source_features", ())
            ):
                continue
            
            disposition = record.get("disposition")
            for column in record.get("bundled_columns", ()):
                if disposition not in ("represented", "collapsed_into", "not_represented"):
                    raise ValueError(
                        f"{database} column {column!r} is documented with an unsupported disposition: {disposition!r}."
                    )
                existing = column_dispositions.get(column)
                if existing is not None and existing != disposition:
                    raise ValueError(
                        f"{database} column {column!r} is documented with conflicting dispositions."
                    )
                column_dispositions[column] = disposition

        documented = set(column_dispositions)
        provided = set(columns)
        if documented != provided:
            undocumented = sorted(provided - documented)
            unmatched = sorted(documented - provided)
            raise ValueError(
                f"{database} mappings must document every bundled feature column exactly once. "
                f"Undocumented columns: {undocumented}. Documented columns not present in the source: {unmatched}."
            )

        return {column: disposition == "represented" for column, disposition in column_dispositions.items()}


    def _removed_operand_features(self):
        """
            Returns the set of typological feature names that should never remain as their own standalone
            public feature, according to "feature_mappings.json". This covers three cases:
            (1) features explicitly tagged with the "removed_urielplus_operand" namespace (operands consumed
            by an exact-collapse computation into "DERIVED");
            (2) bundled columns documented with disposition "not_represented" (columns that map to no
            public feature at all); and
            (3) bundled columns documented only via the historical "urielplus_v1_bundled_conversion_column"
            namespace (old, pre-split v1 column names that may still be present in the released baseline
            data, even though the source CSVs no longer produce them).


            Returns:
                set: The feature names to purge from self.feats[1]/self.data[1].
        """
        self._ensure_feature_mappings()
        removed = set()
        for record in self.feature_mappings:
            for source_feature in record.get("source_features", ()):
                if source_feature.get("namespace") == "removed_urielplus_operand":
                    removed.add(source_feature["id"])

            if record.get("disposition") == "not_represented":
                removed.update(record.get("bundled_columns", ()))
        return removed


    def inferred_features(self):
        """
            Consolidates typological features according to "feature_mappings.json". Exact-collapse rules combine
            several raw operand features into one target using a three-valued OR evaluated across every real
            source. Positive-implication rules propagate a "1" from an antecedent feature to a consequent
            feature, one-way only, applied repeatedly until no value changes (since one rule's output can be
            another rule's input). Both kinds of rule write into a dedicated "DERIVED" pseudo-source, never
            overwriting any real source's own values.

            If caching is enabled, updates the "features.npz" file.
        """
        self._ensure_feature_mappings()

        derived_index = self._get_or_create_derived_source()
        feature_position = {str(feat): idx for idx, feat in enumerate(self.feats[1])}

        logging.info("Inferring feature data based on similar features.....")

        # --- Exact collapse: three-valued OR across named operand features, over every real source ---
        for record in self.feature_mappings:
            if record.get("relationship") != "exact_collapse":
                continue
            operands = [item["id"] for item in record.get("source_features", ())]
            targets = [t for t in record.get("targets", ()) if t.get("matrix") == "typological"]
            if not operands or not targets:
                continue
            if any(op not in feature_position for op in operands):
                continue  # operand not present in this build yet; nothing to collapse

            real_source_indices = [i for i in range(len(self.sources[1])) if i != derived_index]
            operand_indices = [feature_position[op] for op in operands]
            operand_values = self.data[1][:, operand_indices, :][:, :, real_source_indices]

            collapsed = np.where(
                np.any(operand_values == 1, axis=(1, 2)), 1,
                np.where(np.all(operand_values == 0, axis=(1, 2)), 0, -1)
            )

            for target in targets:
                target_feature = target["feature_id"]
                if target_feature not in feature_position:
                    self.data[1] = self._set_new_data_dimensions(self.data[1], [target_feature], [], [])
                    self.feats[1] = np.append(self.feats[1], target_feature)
                    feature_position[target_feature] = len(self.feats[1]) - 1
                    derived_index = self._get_or_create_derived_source()

                target_index = feature_position[target_feature]
                current = self.data[1][:, target_index, derived_index]
                self.data[1][:, target_index, derived_index] = np.maximum(current, collapsed)

        # --- Positive implication: propagate "1" from antecedent to consequent, to a fixpoint ---
        implication_records = [
            record for record in self.feature_mappings
            if record.get("database") == "URIELPLUS" and record.get("relationship") == "positive_implication"
            and any(t.get("matrix") == "typological" for t in record.get("targets", ()))
        ]

        for _ in range(len(implication_records) + 1):
            changed = False
            for record in implication_records:
                antecedents = [item["id"] for item in record.get("source_features", ())]
                targets = [t for t in record.get("targets", ()) if t.get("matrix") == "typological"]
                if len(targets) != 1 or any(a not in feature_position for a in antecedents):
                    continue
                target_feature = targets[0]["feature_id"]
                if target_feature not in feature_position:
                    continue

                antecedent_indices = [feature_position[a] for a in antecedents]
                active = np.any(self.data[1][:, antecedent_indices, :] == 1, axis=(1, 2))

                target_index = feature_position[target_feature]
                update = active & (self.data[1][:, target_index, derived_index] != 1)
                if update.any():
                    self.data[1][update, target_index, derived_index] = 1
                    changed = True
            if not changed:
                break
        else:
            raise ValueError("typological positive-implication rules did not reach a fixed point.")

        removed_operands = self._removed_operand_features()
        redundant_mask = np.isin(self.feats[1], list(removed_operands))
        if redundant_mask.any():
            self.feats[1] = self.feats[1][~redundant_mask]
            self.data[1] = self.data[1][:, ~redundant_mask, :]

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[1]),
                    feats=self.feats[1], data=self.data[1], langs=self.langs[1], sources=self.sources[1])

        self._sync_loaded_features(1)
        self._refresh_indexes(1)

        logging.info("Feature inference complete.")


    def integrate_saphon(self, convert_glottocodes_param=False):
        """
            Updates URIEL+ with data from the updated SAPHON database.


            This function integrates the updated SAPHON data.


            Args:
                convert_glottocodes_param (bool): If True, converts language codes to Glottocodes.
        """
        if self.is_database_incorporated("UPDATED_SAPHON"):
            logging.info("UPDATED_SAPHON already integrated; skipping.")
            return

        logging.info("Importing updated SAPHON from \"saphon_data.csv\"....")

        saphon_data = pd.read_csv(os.path.join(self.cur_dir, "database", "urielplus_csvs", "saphon_data.csv"))

        code_col = "iso_code" if (self.codes == "Iso" and not convert_glottocodes_param) else "glottocode"

        source_index = np.where(self.sources[1] == "PHOIBLE_SAPHON")

        for i, lang in enumerate(saphon_data[code_col]):
            if not pd.isna(lang):
                lang_index = np.where(self.langs[1] == lang)[0][0]
                for feat in saphon_data.columns[2:]:
                    feat_index = np.where(self.feats[1] == feat)
                    self.data[1][lang_index, feat_index, source_index] = saphon_data[feat][i]

        self.sources[1][source_index] = "UPDATED_SAPHON"

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[1]),
                     feats=self.feats[1], data=self.data[1], langs=self.langs[1], sources=self.sources[1])

        logging.info("Updated SAPHON integration complete..")


    def integrate_bdproto(self):
        """
            Updates URIEL+ with data from the BDPROTO database.


            This function integrates the BDPROTO data, converting language codes to Glottocodes if necessary,
            and updates the feature data in URIEL+.
        """
        if self.is_database_incorporated("BDPROTO"):
            logging.info("BDPROTO already integrated; skipping.")
            return

        logging.info("Importing BDPROTO from \"bdproto_data.csv\"....")

        if self.codes == "Iso":
            self.set_glottocodes()

        bdproto_data = pd.read_csv(os.path.join(self.cur_dir, "database", "urielplus_csvs", "bdproto_data.csv"))

        new_langs = self._get_new_languages(self.langs[1], bdproto_data, "language_id")
        new_source = "BDPROTO"

        old_num_langs = self.data[1].shape[0]
        self.data[1] = self._set_new_data_dimensions(self.data[1], [], new_langs, [new_source])

        new_langs_added = 0
        for i, lang in enumerate(bdproto_data["language_id"]):
            lang_index = None
            try:
                lang_index = np.where(self.langs[1] == lang)[0][0]
                if type(lang_index) not in [int, np.int64, float, np.float64]:
                    lang_index = old_num_langs + new_langs_added
                    new_langs_added += 1
            except:
                lang_index = old_num_langs + new_langs_added
                new_langs_added += 1
            for feat in bdproto_data.columns[1:]:
                feat_index = np.where(self.feats[1] == feat)
                self.data[1][lang_index, feat_index, -1] = bdproto_data[feat][i]
        self.langs[1] = np.append(self.langs[1], np.array(new_langs).flatten())
        self.sources[1] = np.append(self.sources[1], new_source)

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[1]),
                     feats=self.feats[1], data=self.data[1], langs=self.langs[1], sources=self.sources[1])
            
        self._calculate_phylogeny_vectors()
        self._calculate_geocoord_vectors()
        self._calculate_script_vectors()

        self._sync_loaded_features(1)
        self._refresh_indexes(1)

        logging.info("BDPROTO integration complete.")


    def integrate_grambank(self):
        """
            Updates URIEL+ with data from the Grambank database.


            This function integrates the Grambank data, converting language codes to Glottocodes if necessary,
            and updates the feature data in URIEL+.
        """
        if self.is_database_incorporated("GRAMBANK"):
            logging.info("GRAMBANK already integrated; skipping.")
            return

        self._ensure_feature_mappings()

        logging.info("Importing Grambank from \"grambank_data.csv\"....")

        if self.codes == "Iso":
            self.set_glottocodes()

        grambank_data = pd.read_csv(os.path.join(self.cur_dir, "database", "urielplus_csvs", "grambank_data.csv"))

        inclusion = self._feature_inclusion_map("GRAMBANK", list(grambank_data.columns[1:]))
        included_columns = [col for col in grambank_data.columns[1:] if inclusion[col]]

        new_feats = self._get_new_features(self.feats[1], included_columns)
        new_langs = self._get_new_languages(self.langs[1], grambank_data, "language_id")
        new_source = "GRAMBANK"

        old_num_langs = self.data[1].shape[0]
        self.data[1] = self._set_new_data_dimensions(self.data[1], new_feats, new_langs, [new_source])

        self.feats[1] = np.append(self.feats[1], new_feats)

        new_langs_added = 0
        for i, lang in enumerate(grambank_data["language_id"]):
            lang_index = None
            try:
                lang_index = np.where(self.langs[1] == lang)[0][0]
                if type(lang_index) not in [int, np.int64, float, np.float64]:
                    lang_index = old_num_langs + new_langs_added
                    new_langs_added += 1
            except:
                lang_index = old_num_langs + new_langs_added
                new_langs_added += 1
            for feat in grambank_data.columns[1:]:
                feat_index = np.where(self.feats[1] == feat)
                self.data[1][lang_index, feat_index, -1] = grambank_data[feat][i]
        self.langs[1] = np.append(self.langs[1], np.array(new_langs).flatten())
        self.sources[1] = np.append(self.sources[1], new_source)

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[1]),
                     feats=self.feats[1], data=self.data[1], langs=self.langs[1], sources=self.sources[1])
            
        self._calculate_phylogeny_vectors()
        self._calculate_geocoord_vectors()
        self._calculate_script_vectors()

        self.inferred_features()

        logging.info("Grambank integration complete.")


    def integrate_apics(self):
        """
            Updates URIEL+ with data from the APiCS database.


            This function integrates the APiCS data, converting language codes to Glottocodes if necessary,
            and updates the feature data in URIEL+.
        """
        if self.is_database_incorporated("APICS"):
            logging.info("APICS already integrated; skipping.")
            return
        
        self._ensure_feature_mappings()

        logging.info("Importing APiCS from \"apics_data.csv\"....")

        if self.codes == "Iso":
            self.set_glottocodes()

        apics_data = pd.read_csv(os.path.join(self.cur_dir, "database", "urielplus_csvs", "apics_data.csv"))

        new_langs = self._get_new_languages(self.langs[1], apics_data, "language_id")

        apics_data = apics_data[["language_id"] + [col for col in apics_data.columns if col != "language_id"]]

        inclusion = self._feature_inclusion_map("APICS", list(apics_data.columns[1:]))
        included_columns = [col for col in apics_data.columns[1:] if inclusion[col]]

        new_feats = self._get_new_features(self.feats[1], included_columns)

        new_source = "APICS"

        old_num_langs = self.data[1].shape[0]
        self.data[1] = self._set_new_data_dimensions(self.data[1], new_feats, new_langs, [new_source])

        self.feats[1] = np.append(self.feats[1], new_feats)

        new_langs_added = 0
        for i, lang in enumerate(apics_data["language_id"]):
            lang_index = None
            try:
                lang_index = np.where(self.langs[1] == lang)[0][0]
                if type(lang_index) not in [int, np.int64, float, np.float64]:
                    lang_index = old_num_langs + new_langs_added
                    new_langs_added += 1
            except:
                lang_index = old_num_langs + new_langs_added
                new_langs_added += 1
            for feat in apics_data.columns[1:]:
                feat_index = np.where(self.feats[1] == feat)

                self.data[1][lang_index, feat_index, -1] = apics_data[feat][i]
        self.langs[1] = np.append(self.langs[1], np.array(new_langs).flatten())
        self.sources[1] = np.append(self.sources[1], new_source)

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[1]),
                     feats=self.feats[1], data=self.data[1], langs=self.langs[1], sources=self.sources[1])

        self._calculate_phylogeny_vectors()
        self._calculate_geocoord_vectors()
        self._calculate_script_vectors()

        self.inferred_features()

        logging.info("APiCS integration complete.")


    def integrate_ewave(self):
        """
            Updates URIEL+ with data from the EWAVE database.


            This function integrates the EWAVE data, converting language codes to Glottocodes if necessary,
            and updates the feature data in URIEL+.
        """
        if self.is_database_incorporated("EWAVE"):
            logging.info("EWAVE already integrated; skipping.")
            return
        
        self._ensure_feature_mappings()

        logging.info("Importing eWAVE from \"english_dialect_data.csv\"....")

        if self.codes == "Iso":
            self.set_glottocodes()

        df = pd.read_csv(os.path.join(os.path.join(self.cur_dir, "database", "urielplus_csvs", "english_dialect_data.csv")))

        inclusion = self._feature_inclusion_map("EWAVE", list(df.columns[1:]))
        included_columns = [col for col in df.columns[1:] if inclusion[col]]

        new_langs = self._get_new_languages(self.langs[1], df, "language_id")
        new_feats = self._get_new_features(self.feats[1], included_columns)
        new_source = "EWAVE"

        old_num_langs = self.data[1].shape[0]
        self.data[1] = self._set_new_data_dimensions(self.data[1], new_feats, new_langs, [new_source])

        self.feats[1] = np.append(self.feats[1], new_feats)

        new_langs_added = 0
        for i, lang in enumerate(df["language_id"]):
            lang_index = None
            try:
                lang_index = np.where(self.langs[1] == lang)[0][0]
                if type(lang_index) not in [int, np.int64, float, np.float64]:
                    lang_index = old_num_langs + new_langs_added
                    new_langs_added += 1
            except:
                lang_index = old_num_langs + new_langs_added
                new_langs_added += 1
            for feat in df.columns[1:]:
                feat_index = np.where(self.feats[1] == feat)
                self.data[1][lang_index, feat_index, -1] = df[feat][i]
        self.langs[1] = np.append(self.langs[1], np.array(new_langs).flatten())
        self.sources[1] = np.append(self.sources[1], new_source)

        if self.cache:
            np.savez(os.path.join(self.cur_dir, "database", self.files[1]),
                     feats=self.feats[1], data=self.data[1], langs=self.langs[1], sources=self.sources[1])

        self._calculate_phylogeny_vectors()
        self._calculate_geocoord_vectors()
        self._calculate_script_vectors()

        self.inferred_features()

        logging.info("eWAVE integration complete.")


    # def integrate_glottolog(self):
    #     """
    #         Updates URIEL+ with data from the Glottolog database.


    #         This function integrates the Glottolog data.
    #     """
    #     logging.info("Importing Glottolog from \"dialects.csv\". This may take a while....")

    #     if self.codes == "Iso":
    #         self.set_glottocodes()
        
    #     glottolog_data = pd.read_csv(os.path.join(self.cur_dir, "database", "urielplus_csvs", "dialects.csv"))

    #     code_cols = ['Language Glot', 'Dialect(s) Glot']

    #     new_langs = set()

    #     for col in code_cols:
    #         for entry in glottolog_data[col].dropna():
    #             parts = [code.strip() for code in entry.split(',') if code.strip()]
    #             new_langs.update(parts)

    #     existing_langs = set(self.langs[1]) if len(self.langs) > 1 else set()
    #     new_langs = sorted(new_langs - existing_langs)

    #     if not new_langs:
    #         logging.info("GLOTTOLOG dialects already integrated; skipping.")
    #         return

    #     self.data[1] = self._set_new_data_dimensions(self.data[1], [], new_langs, [])
    #     self.langs[1] = np.append(self.langs[1], np.array(new_langs).flatten())
        
    #     if self.cache:
    #         np.savez(os.path.join(self.cur_dir, "database", self.files[1]),
    #                  feats=self.feats[1], data=self.data[1], langs=self.langs[1], sources=self.sources[1])

    #     self._calculate_phylogeny_vectors()
    #     self._calculate_geocoord_vectors()
    #     self._calculate_script_vectors()

    #     self._sync_loaded_features(1)
    #     self._refresh_indexes(1)

    #     logging.info("Glottolog integration complete.")


    def integrate_glottolog(self):
        """
        Updates URIEL+ with data from the Glottolog database.

        This function integrates the Glottolog data.
        """
        import time

        start_time = time.time()

        logging.info("=== START integrate_glottolog() ===")
        logging.info('Importing Glottolog from "dialects.csv". This may take a while....')

        # ---------------------------------------------------------
        # Set Glottocodes
        # ---------------------------------------------------------
        if self.codes == "Iso":
            logging.info("self.codes == 'Iso'; calling set_glottocodes()...")
            step_start = time.time()

            self.set_glottocodes()

            logging.info(
                "set_glottocodes() completed in %.2f seconds.",
                time.time() - step_start
            )
        else:
            logging.info("self.codes is already '%s'; skipping set_glottocodes().", self.codes)

        # ---------------------------------------------------------
        # Load Glottolog CSV
        # ---------------------------------------------------------
        logging.info("Reading dialects.csv...")
        step_start = time.time()

        glottolog_data = pd.read_csv(
            os.path.join(
                self.cur_dir,
                "database",
                "urielplus_csvs",
                "dialects.csv"
            )
        )

        logging.info(
            "dialects.csv loaded in %.2f seconds.",
            time.time() - step_start
        )
        logging.info(
            "Glottolog dataframe shape: %s rows x %s columns",
            glottolog_data.shape[0],
            glottolog_data.shape[1]
        )

        # ---------------------------------------------------------
        # Extract Glottolog codes
        # ---------------------------------------------------------
        code_cols = ['Language Glot', 'Dialect(s) Glot']

        logging.info("Extracting Glottolog codes from columns: %s", code_cols)
        step_start = time.time()

        new_langs = set()

        for col in code_cols:
            logging.info("Processing column '%s'...", col)

            entries_processed = 0
            codes_found = 0

            for entry in glottolog_data[col].dropna():
                entries_processed += 1

                parts = [
                    code.strip()
                    for code in entry.split(',')
                    if code.strip()
                ]

                codes_found += len(parts)
                new_langs.update(parts)

            logging.info(
                "Column '%s': processed %d entries, found %d codes.",
                col,
                entries_processed,
                codes_found
            )

        logging.info(
            "Glottolog code extraction completed in %.2f seconds.",
            time.time() - step_start
        )

        logging.info(
            "Total unique Glottolog codes found: %d",
            len(new_langs)
        )

        # ---------------------------------------------------------
        # Compare against existing languages
        # ---------------------------------------------------------
        logging.info("Checking existing languages...")
        step_start = time.time()

        existing_langs = (
            set(self.langs[1])
            if len(self.langs) > 1
            else set()
        )

        logging.info(
            "Existing language count: %d",
            len(existing_langs)
        )

        new_langs = sorted(new_langs - existing_langs)

        logging.info(
            "New languages to integrate: %d",
            len(new_langs)
        )

        logging.info(
            "Language comparison completed in %.2f seconds.",
            time.time() - step_start
        )

        if not new_langs:
            logging.info("GLOTTOLOG dialects already integrated; skipping.")
            logging.info(
                "=== END integrate_glottolog() (%.2f seconds) ===",
                time.time() - start_time
            )
            return

        # ---------------------------------------------------------
        # Add new data dimensions
        # ---------------------------------------------------------
        logging.info(
            "Calling _set_new_data_dimensions() with %d new languages...",
            len(new_langs)
        )
        step_start = time.time()

        self.data[1] = self._set_new_data_dimensions(
            self.data[1],
            [],
            new_langs,
            []
        )

        logging.info(
            "_set_new_data_dimensions() completed in %.2f seconds.",
            time.time() - step_start
        )

        # ---------------------------------------------------------
        # Update language list
        # ---------------------------------------------------------
        logging.info("Appending new languages to self.langs[1]...")
        step_start = time.time()

        self.langs[1] = np.append(
            self.langs[1],
            np.array(new_langs).flatten()
        )

        logging.info(
            "Language list updated in %.2f seconds.",
            time.time() - step_start
        )

        logging.info(
            "New self.langs[1] size: %d",
            len(self.langs[1])
        )

        # ---------------------------------------------------------
        # Save cache
        # ---------------------------------------------------------
        if self.cache:
            logging.info("Saving updated Glottolog data to cache...")
            step_start = time.time()

            np.savez(
                os.path.join(
                    self.cur_dir,
                    "database",
                    self.files[1]
                ),
                feats=self.feats[1],
                data=self.data[1],
                langs=self.langs[1],
                sources=self.sources[1]
            )

            logging.info(
                "Cache saved in %.2f seconds.",
                time.time() - step_start
            )
        else:
            logging.info("self.cache is False; skipping cache save.")

        # ---------------------------------------------------------
        # Calculate phylogeny vectors
        # ---------------------------------------------------------
        logging.info("=== Starting _calculate_phylogeny_vectors() ===")
        step_start = time.time()

        self._calculate_phylogeny_vectors()

        logging.info(
            "=== Finished _calculate_phylogeny_vectors() in %.2f seconds ===",
            time.time() - step_start
        )

        # ---------------------------------------------------------
        # Calculate geographic coordinate vectors
        # ---------------------------------------------------------
        logging.info("=== Starting _calculate_geocoord_vectors() ===")
        step_start = time.time()

        self._calculate_geocoord_vectors()

        logging.info(
            "=== Finished _calculate_geocoord_vectors() in %.2f seconds ===",
            time.time() - step_start
        )

        # ---------------------------------------------------------
        # Calculate script vectors
        # ---------------------------------------------------------
        logging.info("=== Starting _calculate_script_vectors() ===")
        step_start = time.time()

        self._calculate_script_vectors()

        logging.info(
            "=== Finished _calculate_script_vectors() in %.2f seconds ===",
            time.time() - step_start
        )

        # ---------------------------------------------------------
        # Sync loaded features
        # ---------------------------------------------------------
        logging.info("=== Starting _sync_loaded_features(1) ===")
        step_start = time.time()

        self._sync_loaded_features(1)

        logging.info(
            "=== Finished _sync_loaded_features(1) in %.2f seconds ===",
            time.time() - step_start
        )

        # ---------------------------------------------------------
        # Refresh indexes
        # ---------------------------------------------------------
        logging.info("=== Starting _refresh_indexes(1) ===")
        step_start = time.time()

        self._refresh_indexes(1)

        logging.info(
            "=== Finished _refresh_indexes(1) in %.2f seconds ===",
            time.time() - step_start
        )

        # ---------------------------------------------------------
        # Done
        # ---------------------------------------------------------
        logging.info(
            "=== Glottolog integration complete. Total time: %.2f seconds ===",
            time.time() - start_time
        )


    def integrate_databases(self):
        """
            Updates URIEL+ with data from all available databases (UPDATED_SAPHON, BDPROTO, GRAMBANK, APICS, EWAVE, GLOTTOLOG).
        """
        logging.info("Importing all databases....")

        databases = {
            "UPDATED_SAPHON": self.integrate_saphon,
            "BDPROTO": self.integrate_bdproto,
            "GRAMBANK": self.integrate_grambank,
            "APICS": self.integrate_apics,
            "EWAVE": self.integrate_ewave,
        }
       
        for db, integrate_method in databases.items():
            if not self.is_database_incorporated(db):
                integrate_method()

        self.integrate_glottolog()
        self.inferred_features()

        logging.info("All databases integration complete.")


    def integrate_custom_databases(self, *args):
        """
            Updates URIEL+ based on provided databases.


            Args:
                *args: Databases to update URIEL+ with.


            Raises:
                KeyError: If a provided database name is invalid.
        """
        logging.info("Importing custom databases....")

        if len(args) == 1 and isinstance(args[0], list):
            databases = args[0]
        else:
            databases = list(args)

        valid_databases = {
            "UPDATED_SAPHON": self.integrate_saphon,
            "BDPROTO": self.integrate_bdproto,
            "GRAMBANK": self.integrate_grambank,
            "APICS": self.integrate_apics,
            "EWAVE": self.integrate_ewave,
            "GLOTTOLOG": self.integrate_glottolog,
            "INFERRED": self.inferred_features,
        }

        for db in databases:
            if db not in valid_databases:
                raise KeyError(f"Unknown database: {db}. Valid databases are {list(valid_databases.keys())}.")
            if db == "GLOTTOLOG" or not self.is_database_incorporated(db):
                valid_databases[db]()
           
        logging.info("Custom databases integration complete.")
