from urielplus import urielplus


def main():
    print("=" * 80)
    print("URIEL+ FUNCTION TEST")
    print("=" * 80)

    # ------------------------------------------------------------------
    # Initialize
    # ------------------------------------------------------------------
    print("\n[1] INITIALIZATION")
    print("-" * 80)

    u = urielplus.URIELPlus()

    print("URIEL+ initialized successfully.")

    # ------------------------------------------------------------------
    # Configuration Options
    # ------------------------------------------------------------------
    print("\n[2] CONFIGURATION OPTIONS")
    print("-" * 80)

    # Get default configurations
    print("Default cache:", u.get_cache())
    print("Default aggregation:", u.get_aggregation())
    print("Default fill_with_base_lang:", u.get_fill_with_base_lang())
    print("Default distance metric:", u.get_distance_metric())

    # Change configurations
    print("\nChanging configurations...")

    u.set_cache(True)
    print("Cache:", u.get_cache())

    u.set_aggregation("A")
    print("Aggregation:", u.get_aggregation())

    u.set_fill_with_base_lang(False)
    print("Fill with base language:", u.get_fill_with_base_lang())

    u.set_distance_metric("cosine")
    print("Distance metric:", u.get_distance_metric())

    # Restore the README defaults
    print("\nRestoring default configurations...")

    u.set_cache(False)
    u.set_aggregation("U")
    u.set_fill_with_base_lang(True)
    u.set_distance_metric("angular")

    print("Cache:", u.get_cache())
    print("Aggregation:", u.get_aggregation())
    print("Fill with base language:", u.get_fill_with_base_lang())
    print("Distance metric:", u.get_distance_metric())

    # ------------------------------------------------------------------
    # Retrieving Loaded Features
    # ------------------------------------------------------------------
    print("\n[3] RETRIEVING LOADED FEATURES")
    print("-" * 80)

    vector_types = [
        "phylogeny",
        "typological",
        "geography",
        "scriptural",
    ]

    feature_types = [
        "features",
        "languages",
        "data",
        "sources",
    ]

    for vector_type in vector_types:
        for feature_type in feature_types:
            function_name = f"get_{vector_type}_{feature_type}_array"

            print(f"\nTesting {function_name}()")

            try:
                function = getattr(u, function_name)
                result = function()

                print("  SUCCESS")
                print("  Type:", type(result))

                try:
                    print("  Shape:", result.shape)
                except AttributeError:
                    try:
                        print("  Length:", len(result))
                    except TypeError:
                        pass

            except Exception as e:
                print("  FAILED")
                print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Database Integration
    # ------------------------------------------------------------------
    print("\n[4] DATABASE INTEGRATION")
    print("-" * 80)

    # Individual databases
    databases = [
        "saphon",
        "bdproto",
        "grambank",
        "apics",
        "ewave",
        "glottolog",
    ]

    for database in databases:
        function_name = f"integrate_{database}"

        print(f"\nTesting {function_name}()")

        try:
            function = getattr(u, function_name)
            result = function()

            print("  SUCCESS")
            print("  Return value:", result)

        except Exception as e:
            print("  FAILED")
            print("  Error:", type(e).__name__, "-", e)

    # Custom database integration
    print("\nTesting integrate_custom_databases()")

    try:
        result = u.integrate_custom_databases(
            ["UPDATED_SAPHON", "BDPROTO", "EWAVE"]
        )

        print("  SUCCESS")
        print("  Return value:", result)

    except Exception as e:
        print("  FAILED")
        print("  Error:", type(e).__name__, "-", e)

    # Integrate all databases
    print("\nTesting integrate_databases()")

    try:
        result = u.integrate_databases()

        print("  SUCCESS")
        print("  Return value:", result)

    except Exception as e:
        print("  FAILED")
        print("  Error:", type(e).__name__, "-", e)

    # Set Glottocodes
    print("\nTesting set_glottocodes()")

    try:
        result = u.set_glottocodes()

        print("  SUCCESS")
        print("  Return value:", result)

    except Exception as e:
        print("  FAILED")
        print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    print("\n[5] RESET")
    print("-" * 80)

    try:
        result = u.reset()

        print("reset() SUCCESS")
        print("Return value:", result)

    except Exception as e:
        print("reset() FAILED")
        print("Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Imputation
    # ------------------------------------------------------------------
    print("\n[6] IMPUTATION")
    print("-" * 80)

    # Test aggregation
    print("\nTesting set_aggregation() + aggregate()")

    try:
        u.set_aggregation("U")
        result = u.aggregate()

        print("  SUCCESS")
        print("  Aggregation:", u.get_aggregation())
        print("  Return value:", result)

    except Exception as e:
        print("  FAILED")
        print("  Error:", type(e).__name__, "-", e)

    # Test each imputation strategy
    imputation_strategies = [
        "midaspy",
        "knn",
        "softimpute",
        "mean",
    ]

    for strategy in imputation_strategies:
        function_name = f"{strategy}_imputation"

        print(f"\nTesting {function_name}()")

        try:
            function = getattr(u, function_name)
            result = function()

            print("  SUCCESS")
            print("  Return value:", result)

        except Exception as e:
            print("  FAILED")
            print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Language Distance Calculations
    # ------------------------------------------------------------------
    print("\n[7] LANGUAGE DISTANCE CALCULATIONS")
    print("-" * 80)

    language_1 = "stan1293"
    language_2 = "hind1269"

    # Distance types
    distance_types = [
        "genetic",
        "syntactic",
        "featural",
        "phonological",
        "inventory",
        "geographic",
        "morphological",
        "script",
    ]

    # Test new_distance()
    print("\nTesting new_distance()")

    for distance_type in distance_types:
        print(f"\n  {distance_type}")

        try:
            result = u.new_distance(
                distance_type,
                [language_1, language_2]
            )

            print("    SUCCESS")
            print("    Result:", result)

        except Exception as e:
            print("    FAILED")
            print("    Error:", type(e).__name__, "-", e)

    # Test multiple distance types
    print("\nTesting new_distance() with multiple distance types")

    try:
        result = u.new_distance(
            ["syntactic", "phonological"],
            [language_1, language_2]
        )

        print("  SUCCESS")
        print("  Result:", result)

    except Exception as e:
        print("  FAILED")
        print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Custom Distance
    # ------------------------------------------------------------------
    print("\n[8] CUSTOM DISTANCE")
    print("-" * 80)

    features = [
        "F_Germanic",
        "S_SVO",
        "P_NASAL_VOWELS",
    ]

    sources = [
        "WALS",
        "A",
    ]

    for source in sources:
        print(f"\nTesting new_custom_distance() with source={source}")

        try:
            # NOTE: `source` must be passed as a keyword argument.
            # new_custom_distance's real signature is
            # (self, features, *args, source='A'), so passing source
            # positionally causes it to be swallowed into *args along
            # with the language list, breaking the language parsing.
            result = u.new_custom_distance(
                features,
                [language_1, language_2],
                source=source
            )

            print("  SUCCESS")
            print("  Result:", result)

        except Exception as e:
            print("  FAILED")
            print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Language Vectors
    # ------------------------------------------------------------------
    print("\n[9] LANGUAGE VECTORS")
    print("-" * 80)

    # README says distance_type must be a single distance type
    for distance_type in distance_types:
        print(f"\nTesting get_vector('{distance_type}', ...)")

        try:
            result = u.get_vector(
                distance_type,
                [language_1, language_2]
            )

            print("  SUCCESS")
            print("  Type:", type(result))

            try:
                print("  Shape:", result.shape)
            except AttributeError:
                try:
                    print("  Length:", len(result))
                except TypeError:
                    pass

        except Exception as e:
            print("  FAILED")
            print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Feature Coverage
    # ------------------------------------------------------------------
    print("\n[10] FEATURE COVERAGE")
    print("-" * 80)

    # Option A: all_feature_coverage() - no arguments, prints coverage
    # for every resource level and every distance type. This is the
    # behavior the README documents as `feature_coverage()`.
    print("\nTesting all_feature_coverage()")

    try:
        result = u.all_feature_coverage()

        print("  SUCCESS")
        print("  Return value:", result)

    except Exception as e:
        print("  FAILED")
        print("  Error:", type(e).__name__, "-", e)

    # Option B: feature_coverage(resource_level, distance_type) - the
    # newer, targeted function. Requires a resource level
    # ("high-resource", "medium-resource", or "low-resource") and a
    # distance type. Loop over combinations to exercise it broadly.
    resource_levels = [
        "high-resource",
        "medium-resource",
        "low-resource",
    ]

    for resource_level in resource_levels:
        for distance_type in distance_types:
            print(f"\nTesting feature_coverage('{resource_level}', '{distance_type}')")

            try:
                result = u.feature_coverage(resource_level, distance_type)

                print("  SUCCESS")
                print("  Result:", result)

            except Exception as e:
                print("  FAILED")
                print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Confidence Scores
    # ------------------------------------------------------------------
    print("\n[11] CONFIDENCE SCORES")
    print("-" * 80)

    for distance_type in distance_types:
        print(f"\nTesting confidence_score() for {distance_type}")

        try:
            result = u.confidence_score(
                language_1,
                language_2,
                distance_type
            )

            print("  SUCCESS")
            print("  Result:", result)

        except Exception as e:
            print("  FAILED")
            print("  Error:", type(e).__name__, "-", e)

    # ------------------------------------------------------------------
    # Finish
    # ------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("URIEL+ FUNCTION TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()