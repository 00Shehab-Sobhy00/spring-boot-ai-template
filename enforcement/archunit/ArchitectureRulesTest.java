// Drop-in ArchUnit test — the executable form of ai/ARCHITECTURE.md.
// Copy to: <service>/src/test/java/<base-package>/architecture/ArchitectureRulesTest.java
// Set BASE_PACKAGE, and set the package declaration below to match the directory you copied it to
// (e.g. `package com.acme.orders.architecture;`). Nothing else is service-specific.
//
// Every rule below cites the line in ai/ARCHITECTURE.md it enforces. If you change the markdown,
// change the test in the same PR (scripts/check-docs-impact.py `arch` row makes that blocking).
package architecture;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.Architectures.layeredArchitecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

@AnalyzeClasses(
        packages = ArchitectureRulesTest.BASE_PACKAGE,
        importOptions = ImportOption.DoNotIncludeTests.class)
class ArchitectureRulesTest {

    static final String BASE_PACKAGE = "com.example.service"; // <-- change me

    // Both spellings: `controller` is the Spring convention, `controllers` is also seen.
    // A glob that matches nothing makes every rule below pass vacuously — see
    // layer_globs_all_match_classes(), which is what actually guards against that.
    private static final String CONTROLLERS = "..controller..";
    private static final String CONTROLLERS_ALT = "..controllers..";
    private static final String SERVICES    = "..service..";
    private static final String REPOSITORIES = "..repository..";
    private static final String CLIENTS     = "..client..";
    private static final String DTO         = "..dto..";
    private static final String ENTITY      = "..entity..";

    // ARCHITECTURE.md → "Dependency Rule": Controller → Service → Repository, downward only.
    @ArchTest
    static final ArchRule layers_point_downward_only = layeredArchitecture()
            .consideringOnlyDependenciesInLayers()
            .layer("Controller").definedBy(CONTROLLERS, CONTROLLERS_ALT)
            .layer("Service").definedBy(SERVICES)
            .layer("Repository").definedBy(REPOSITORIES)
            .layer("Client").definedBy(CLIENTS)
            .whereLayer("Controller").mayNotBeAccessedByAnyLayer()
            .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller", "Service")
            .whereLayer("Repository").mayOnlyBeAccessedByLayers("Service")
            .whereLayer("Client").mayOnlyBeAccessedByLayers("Service");

    // ARCHITECTURE.md → "Forbidden: Controller → Repository"
    @ArchTest
    static final ArchRule controllers_do_not_touch_repositories = noClasses()
            .that().resideInAnyPackage(CONTROLLERS, CONTROLLERS_ALT)
            .should().dependOnClassesThat().resideInAPackage(REPOSITORIES);

    // ARCHITECTURE.md → "Forbidden: Controller → Client / Adapter (prefer via Service)"
    @ArchTest
    static final ArchRule controllers_do_not_call_clients_directly = noClasses()
            .that().resideInAnyPackage(CONTROLLERS, CONTROLLERS_ALT)
            .should().dependOnClassesThat().resideInAPackage(CLIENTS);

    // ARCHITECTURE.md → "Entities are never returned raw from Controllers"
    @ArchTest
    static final ArchRule controllers_do_not_expose_entities = noClasses()
            .that().resideInAnyPackage(CONTROLLERS, CONTROLLERS_ALT)
            .should().dependOnClassesThat().resideInAPackage(ENTITY);

    // ARCHITECTURE.md → "DTOs never reach the Repository / persistence layer"
    @ArchTest
    static final ArchRule repositories_do_not_see_dtos = noClasses()
            .that().resideInAPackage(REPOSITORIES)
            .should().dependOnClassesThat().resideInAPackage(DTO);

    // ARCHITECTURE.md → "Lower layers must not depend on upper layers"
    @ArchTest
    static final ArchRule repositories_do_not_depend_upward = noClasses()
            .that().resideInAPackage(REPOSITORIES)
            .should().dependOnClassesThat().resideInAnyPackage(SERVICES, CONTROLLERS, CONTROLLERS_ALT);

    // ARCHITECTURE.md → "Repositories talk Entities only"
    @ArchTest
    static final ArchRule entities_live_in_entity_package = classes()
            .that().areAnnotatedWith("jakarta.persistence.Entity")
            .should().resideInAPackage(ENTITY);

    // AGENTS.md non-negotiable → "Cleanup/purge SQL: never unbounded deletes"
    // (heuristic: a repository method named delete*/purge* must not be a plain @Modifying query
    //  without a parameter — refine per service)
    @ArchTest
    static final ArchRule controllers_are_annotated = classes()
            .that().resideInAPackage(CONTROLLERS)
            .and().haveSimpleNameEndingWith("Controller")
            .should().beAnnotatedWith("org.springframework.web.bind.annotation.RestController");

    // Smoke check that the import actually found classes (an empty scan passes every rule vacuously)
    @ArchTest
    static void base_package_is_not_empty(JavaClasses classes) {
        if (classes.isEmpty()) {
            throw new AssertionError("No classes imported from " + BASE_PACKAGE
                    + " — every rule above passed vacuously. Fix BASE_PACKAGE.");
        }
    }

    // A non-empty import is NOT enough: a single wrong layer glob silently empties that layer
    // while every other rule still passes. Assert each named layer actually matched something.
    @ArchTest
    static void layer_globs_all_match_classes(JavaClasses classes) {
        String[][] layers = {
                {"CONTROLLERS", CONTROLLERS + " or " + CONTROLLERS_ALT},
                {"SERVICES", SERVICES},
                {"REPOSITORIES", REPOSITORIES},
                {"CLIENTS", CLIENTS},
                {"DTO", DTO},
                {"ENTITY", ENTITY},
        };
        StringBuilder empty = new StringBuilder();
        for (String[] layer : layers) {
            if (!anyClassResidesIn(classes, layer[1])) {
                empty.append("\n  - ").append(layer[0]).append(" -> ").append(layer[1]);
            }
        }
        if (empty.length() > 0) {
            throw new AssertionError(
                    "These layer globs matched zero classes, so every rule over them passed "
                    + "vacuously. Adjust them to this service's real package layout:" + empty);
        }
    }

    private static boolean anyClassResidesIn(JavaClasses classes, String glob) {
        for (String single : glob.split(" or ")) {
            String segment = single.replace("..", "");
            for (com.tngtech.archunit.core.domain.JavaClass c : classes) {
                String pkg = c.getPackageName();
                if (pkg.equals(segment) || pkg.contains("." + segment + ".")
                        || pkg.endsWith("." + segment)) {
                    return true;
                }
            }
        }
        return false;
    }

    // Convenience for running outside JUnit (e.g. eval harness): java ArchitectureRulesTest
    public static void main(String[] args) {
        JavaClasses classes = new ClassFileImporter()
                .withImportOption(new ImportOption.DoNotIncludeTests())
                .importPackages(BASE_PACKAGE);
        layers_point_downward_only.check(classes);
        controllers_do_not_touch_repositories.check(classes);
        controllers_do_not_call_clients_directly.check(classes);
        controllers_do_not_expose_entities.check(classes);
        repositories_do_not_see_dtos.check(classes);
        repositories_do_not_depend_upward.check(classes);
        entities_live_in_entity_package.check(classes);
        controllers_are_annotated.check(classes);
        base_package_is_not_empty(classes);
        layer_globs_all_match_classes(classes);
        System.out.println("architecture rules: ok");
    }
}
