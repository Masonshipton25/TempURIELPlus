# Implemented Changes

## urielplus.py
- Renamed "scriptural" → "script" throughout
- Fixed `set_*_loaded_features` wrapper bug (extra `self` argument)
- Added linguistic/geographic data validation on load and in `set_loaded_features`
- Fixed `codes` assignment (passed via `BaseURIEL.__init__`, no longer computed-then-overwritten)
- Simplified `reset()`
- Replaced `sys.exit(1)` with raised exceptions
- `self.databases`/`self.imputation`/`self.querying` now alias `self` instead of separate instances
- Added `_refresh_indexes` (name-to-position lookup tables)
- Added `_sync_loaded_features` (keeps `self.loaded_features` in sync with mutated arrays)
- Added dtype casting (`int8`/`float32`) on load
- Removed `query_yes_no` (dead code)

## base_uriel.py
- Added `codes` parameter to `__init__`, with validation
- Split `get_codes()` (returns stored state) from `_infer_codes()` (fallback auto-detection)
- Replaced `sys.exit(1)` with raised exceptions in all setters
- Removed `self.dialects` side-effect from `set_fill_with_base_lang`
- Rewrote `set_glottocodes` (column rename, literal-"nan" preservation fix, duplicate rejection, blank-value filtering, dict-based mapping, sync/refresh calls)
- Replaced `sys.exit(1)` with raised exception in `get_dialects`
- Removed unused `self.logger`
- Removed unused `import sys`

## urielplus_databases.py
- Fixed `is_database_incorporated` (Glottolog no longer blocks all other checks; returns bool instead of exiting)
- CSV column renames across SAPHON, BDPROTO, Grambank, APiCS, eWAVE, script, and lang/family/geo source files
- Rewrote `_calculate_phylogeny_vectors` (path-qualified lineage features, full-ancestor marking, dynamic column creation, duplicate-lineage-row resolution)
- Rewrote `_calculate_geocoord_vectors` (fixed antipodal-distance normalization, `-1` instead of `NaN` for missing coordinates)
- Rewrote `_calculate_script_vectors` (dynamic column creation, name-based lookup instead of positional assumption)
- Rewrote `integrate_glottolog` (no longer gated by source presence; gated by dialect-expansion completeness)
- Fixed `integrate_databases`/`integrate_custom_databases` dispatch logic
- Removed `combine_features`, `_load_duplicate_feature_sets`, `_ensure_duplicate_feature_sets` (dead code)
- Added `_load_feature_mappings`/`_ensure_feature_mappings`
- Added `_get_or_create_derived_source`
- Added `inferred_features` (exact-collapse three-valued OR + positive-implication fixpoint propagation into "DERIVED" source)
- Added `_move_derived_to_end`
- Added hardcoded redundant-feature purge list, applied in `inferred_features` (**THIS NEEDS TO BE CHANGED**)
- Replaced `sys.exit(1)` with raised exceptions throughout
- Added `_sync_loaded_features`/`_refresh_indexes` calls to all functions that reassign feature/language/source arrays
- Removed unused `import sys`

## urielplus_querying.py
- Renamed "scriptural" → "script" throughout
- Fixed `get_vector` (feature-position/language-position index bug)
- Added missing-value exclusion masking (`_known_values` helper) to aggregation and confidence functions
- Added geographic-specific averaging override (bypasses union aggregation)
- Fixed union aggregation logic in `_process_language`/`_process_custom_language`
- Replaced hardcoded feature-offset boundaries with dynamic resolution (`_resolve_custom_feature_index`)
- Added script matrix to custom distance requests
- Fixed source-classifier bypass list (geographic/script prefixes)
- Converted list membership checks to set membership in `feature_coverage`/`all_feature_coverage`
- Fixed indentation bug in `featural_confidence_score`'s `check_agreement`
- Replaced `sys.exit(1)` with raised exceptions throughout
- Removed unused `import sys`

## urielplus_imputation.py
- Converted pandas/contexttimer/fancyimpute/joblib/scikit-learn imports to lazy, module-level loading
- Added Python-version gating for MIDASpy (3.10 only)
- Added scikit-learn compatibility shim for SoftImpute (`force_all_finite`/`ensure_all_finite`)
- Replaced `sys.exit(1)` with raised exceptions throughout
