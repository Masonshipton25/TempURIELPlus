# Changelog

## Release Notes

### 🐛 Bug Fixes
- Fixed a bug in the `set_*_loaded_features` wrapper that passed an extra `self` argument
- Fixed incorrect assignment of `codes` (was being computed and then overwritten instead of passed through `BaseURIEL.__init__`)
- Fixed `is_database_incorporated` so a missing Glottolog database no longer blocks all other incorporation checks
- Fixed antipodal-distance normalization in geographic coordinate vector calculation
- Fixed a feature-position/language-position indexing bug in `get_vector`
- Fixed union aggregation logic in `_process_language` and `_process_custom_language`
- Fixed the source-classifier bypass list to correctly handle geographic and script prefixes
- Fixed an indentation bug in `featural_confidence_score`'s `check_agreement`
- Fixed dispatch logic in `integrate_databases`/`integrate_custom_databases`
- Fixed a literal-"nan" preservation issue and added duplicate rejection and blank-value filtering in `set_glottocodes`

### ✨ Improvements
- Replaced all `sys.exit(1)` calls across the codebase with proper raised exceptions
- Added linguistic and geographic data validation on load and in `set_loaded_features`
- Added `codes` parameter (with validation) to `BaseURIEL.__init__`
- Added dtype casting (`int8`/`float32`) on data load
- Added `_refresh_indexes` for name-to-position lookup tables
- Added `_sync_loaded_features` to keep `loaded_features` in sync with mutated arrays, now called throughout wherever feature/language/source arrays are reassigned
- Added missing-value exclusion masking (`_known_values` helper) to aggregation and confidence functions
- Added a geographic-specific averaging override that bypasses union aggregation
- Added script matrix support to custom distance requests
- Added dynamic resolution of feature-offset boundaries via `_resolve_custom_feature_index`, replacing hardcoded boundaries
- Added `_load_feature_mappings`/`_ensure_feature_mappings` and `_get_or_create_derived_source`
- Added `inferred_features`: exact-collapse three-valued OR with positive-implication fixpoint propagation into a "DERIVED" source
- Converted list membership checks to set membership in `feature_coverage`/`all_feature_coverage`
- Converted pandas, contexttimer, fancyimpute, joblib, and scikit-learn imports to lazy, module-level loading
- Added Python-version gating for MIDASpy (restricted to 3.10)
- Added a scikit-learn compatibility shim for SoftImpute (`force_all_finite`/`ensure_all_finite`)
- Rewrote `_calculate_phylogeny_vectors` with path-qualified lineage features, full-ancestor marking, dynamic column creation, and duplicate-lineage-row resolution
- Rewrote `_calculate_script_vectors` with dynamic column creation and name-based (rather than positional) lookup
- Rewrote `integrate_glottolog` to be gated by dialect-expansion completeness rather than source presence
- Rewrote `set_glottocodes` with column renaming and dict-based mapping
- Renamed "scriptural" → "script" throughout `urielplus.py` and `urielplus_querying.py`
- Renamed CSV columns across SAPHON, BDPROTO, Grambank, APiCS, eWAVE, script, and lang/family/geo source files
- Simplified `reset()`
- `self.databases`, `self.imputation`, and `self.querying` now alias `self` instead of maintaining separate instances

### 🧹 Removed
- Removed `query_yes_no` (dead code)
- Removed `combine_features`, `_load_duplicate_feature_sets`, and `_ensure_duplicate_feature_sets` (dead code)
- Removed the `self.dialects` side-effect from `set_fill_with_base_lang`
- Removed unused `self.logger`
- Removed unused `import sys` statements
