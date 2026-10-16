# SSRC-IBMS Browser UAT Supplemental Remediation Register

**Project:** CDCS-EMP / SSRC Integrated Business Management System (SSRC-IBMS)
**Parent baseline:** `SSRC-IBMS-BROWSER-UAT-REMEDIATION-BASELINE.md`
**Related roadmap:** `SSRC-IBMS-PILOT-READINESS-IMPLEMENTATION-ROADMAP-V1.md`
**Register status:** ACTIVE — investigation and reconciliation
**Application-code changes authorized by this register:** None by default
**Database changes authorized by this register:** None
**Git staging or commits authorized by this register:** None

---

## 1. Purpose

This register tracks supplemental Browser UAT findings, verification tasks, and reconciliation work discovered while investigating the current pilot workflow.

It exists to maintain a clear, evidence-based record without duplicating or silently revising the approved Browser UAT Remediation Baseline.

The register is an operational tracking record. It does not independently approve architecture changes, application changes, database operations, controlled-data preparation, or Gate 6 acceptance.

## 2. Document authority and boundaries

The following records retain their existing purposes and authority:

| Record | Responsibility |
|---|---|
| `SSRC-IBMS-BROWSER-UAT-REMEDIATION-BASELINE.md` | Authoritative Browser UAT baseline, historical findings UAT-R01–R12, remediation principles, controlled-data requirements, and Gate 6 conditions |
| `CDCS-EMP-WORKFLOW-RULES-REGISTER.md` | Workflow rules and decisions recorded there |
| `SSRC-IBMS-ICRC-WORKSHOP-UAT-EXECUTION-LOG.md` | ICRC workshop UAT execution evidence |
| `SSRC-IBMS-ICRC-WORKSHOP-DEMONSTRATION-SCENARIO.md` | ICRC demonstration scenario |
| `SSRC-IBMS-PILOT-READINESS-IMPLEMENTATION-ROADMAP-V1.md` | Pilot readiness roadmap and implementation sequencing |
| This register | Supplemental findings, evidence, investigation tasks, uncommitted-work reconciliation, and closure tracking |

The related workflow and workshop records must remain unchanged unless their modification is separately authorized.

This register supplements UAT-R01–R12. It does not replace, renumber, close, or reopen those findings. Where a supplemental finding overlaps an existing item, record the relationship and reconcile it against the baseline before creating duplicate remediation work.

## 3. Status and evidence rules

Use the following statuses:

- **Confirmed:** direct evidence establishes the stated defect or gap.
- **Investigating:** available evidence is insufficient to determine the correct outcome.
- **Deferred:** the observation is valid but is not currently authorized for implementation.
- **Blocked:** progress requires an approval, prerequisite, or decision.
- **Ready for verification:** an authorized change or investigation outcome is ready for focused testing.
- **Verified:** the stated acceptance criteria passed with recorded evidence.
- **Closed:** verification and any required reconciliation are complete.

A capability missing from the visible browser interface is not automatically a backend defect. A missing test file is not proof that no coverage exists. Blank optional fields are not automatically validation defects. Do not invent expected values or change existing UAT data merely to produce a successful result.

Every finding must identify its evidence, remaining uncertainty, next action, and closure criteria.

## 4. Supplemental findings

### SUP-01 — Purchase Request status can be edited as ordinary form data

**Classification:** Confirmed UI/service-boundary inconsistency
**Status:** Ready for verification — automated regression passed; browser confirmation pending
**Priority:** High
**Related areas:** Procurement Purchase Requests; workflow enforcement

**Evidence recorded**
- The Purchase Request edit form renders `form.status` as an ordinary text field.
- The edit route directly assigns the submitted form status to the Purchase Request.
- `PurchaseRequestService` provides workflow transition methods, including `submit`, `approve`, `reject`, and `return_to_draft`.
- `PurchaseRequestWorkflow` defines the expected states and transitions.
- The form documentation states that workflow lifecycle transitions belong to a dedicated workflow stage.

**Required investigation**
1. Establish the intended authorization and workflow-action pattern from the existing Procurement architecture.
2. Inspect the edit route, form, service, workflow, permission checks, and relevant tests together.
3. Determine how direct status edits should be prevented without bypassing the established service boundary.
4. Identify the appropriate focused regression tests before proposing an implementation.

**Acceptance criteria**
- Ordinary editing cannot bypass the approved Purchase Request workflow.
- Workflow transitions enforce valid source and target states.
- Authorization failures and invalid transitions are handled safely.
- Tests verify both permitted transitions and rejected bypass attempts.
- Existing Purchase Request records remain unchanged during investigation.

### SUP-02 — Purchase Request workflow actions are not evident in the reviewed browser journey

**Classification:** Browser workflow integration gap; intended delivery stage to verify
**Status:** Ready for verification — automated regression passed; browser confirmation pending
**Priority:** High
**Related finding:** SUP-01

**Evidence recorded**
- The reviewed Purchase Request detail page exposes Edit Purchase Request and Back to Purchase Requests.
- The Purchase Request list did not expose visible row actions in the reviewed session.
- The service and workflow contain transition operations.
- No Purchase Request submit/approve route was found during the initial route inspection.

**Required investigation**
- Confirm whether workflow actions are intended to be available in the current delivery stage.
- Review route registration, endpoint permissions, templates, navigation, and workflow conventions.
- Determine the correct user-visible actions for each authorized state.
- Avoid adding actions that bypass service-layer workflow enforcement.

**Acceptance criteria**
- The expected actions are documented against the workflow and permission model.
- Each authorized action invokes the correct service operation.
- Invalid-state actions are not offered or are safely rejected.
- Browser verification demonstrates the resulting state and unauthorized-access behavior.

### SUP-03 — Purchase Request route-test coverage needs a complete, focused inventory

**Classification:** Test discovery gap
**Status:** Closed — focused route-test inventory completed; no obvious core-handler coverage gap found
**Priority:** High
**Related findings:** SUP-01, SUP-02

**Evidence recorded**
- An initial search did not locate test filenames matching the Purchase Request route naming pattern.
- A workflow-related search found a reference in `tests/modules/procurement/services/test_purchase_flow.py`.
- The initial search does not establish that route coverage is absent from all other test files.

**Required investigation**
- Search for Purchase Request endpoint names and route behavior across the relevant test tree.
- Identify coverage for create, edit, view, delete, line management, permissions, status changes, and workflow actions.
- Reuse the repository's existing route-test conventions.

**Acceptance criteria**
- A coverage inventory identifies existing tests and verified gaps.
- Any missing tests are added only with separately authorized application/test changes.
- Focused tests cover the confirmed behavior without mutating the live UAT database.

### SUP-04 — Purchase Request estimated cost fields are blank

**Classification:** Data/form behavior investigation
**Status:** Ready for verification — approved usability clarification implemented and form tests passed
**Priority:** Medium
**Related areas:** Procurement Purchase Request lines; cost estimation

**Evidence recorded**
- The reviewed line contains quantity 60 and unit `bottles`.
- Estimated Unit Cost and Estimated Total were blank.
- No unit price was supplied during the recorded browser workflow.

**Required investigation**
- Establish whether the fields are optional.
- Inspect form validators, service calculations, model constraints, and template behavior.
- Determine whether Estimated Total should be calculated when a unit cost is supplied.
- Do not invent a price or update the existing line solely to make the fields nonblank.

**Acceptance criteria**
- Required and optional fields are documented accurately.
- Any expected calculation is demonstrated with a controlled test fixture or otherwise authorized test data.
- The existing UAT record is preserved unless separate data-change authorization is granted.

### SUP-05 — Purchase Request list and detail action discoverability

**Classification:** Browser usability observation
**Status:** Ready for verification — permission-visibility regression passed; browser confirmation pending
**Priority:** Medium
**Related areas:** Procurement navigation and action discoverability

**Evidence recorded**
- The reviewed list showed a New Purchase Request action but no visible row actions.
- The detail page exposed Edit Purchase Request and Back to Purchase Requests.
- The correct actions may depend on state, permissions, or delivery-stage boundaries.

**Required investigation**
- Compare list/detail actions with existing authorization and workflow conventions.
- Distinguish a genuine navigation gap from intentionally restricted actions.
- Coordinate any proposed changes with SUP-02.

**Acceptance criteria**
- Expected actions are documented by state and permission.
- Any approved usability change preserves authorization and workflow boundaries.
- Browser evidence demonstrates the final action visibility and destinations.

### SUP-06 — Catering Purchase Requirement to Procurement Purchase Request progression

**Classification:** Cross-module workflow verification
**Status:** Closed — intended cross-module progression confirmed; no defect established
**Priority:** High
**Related areas:** Catering Purchase Requirement, Procurement Purchase Requirement, Purchase Request

**Evidence recorded**
- Catering Purchase Requirement #4 was handed off to Procurement.
- A Procurement Purchase Requirement was created from the Catering-originated requirement.
- A Purchase Request was subsequently created manually from that Procurement Purchase Requirement.
- A Purchase Flow coordinator exists for Purchase Requirement-to-Purchase Request progression.

**Required investigation**
- Establish the intended browser journey and whether coordinator-driven progression should be exposed.
- Verify source references, ownership boundaries, and duplicate-prevention behavior.
- Establish how retries and repeated handoffs should behave.
- Preserve the existing records and reference chain.

**Acceptance criteria**
- The expected progression is documented against the architecture and service contracts.
- Duplicate handoffs or requests are handled according to the approved idempotency rules.
- Catering retains business-layer ownership; Procurement retains purchase workflow ownership.
- Verification uses safe test data and does not duplicate existing UAT business records.

### SUP-07 — Purchase Requirement selection and eligibility filtering

**Classification:** Query and usability investigation
**Status:** Deferred — no confirmed defect; eligibility rules require clarification before further action
**Priority:** Medium
**Related areas:** Procurement forms and Purchase Requirement selection

**Evidence recorded**
- An initial inspection observed a Purchase Requirement choice list configured with a limit of up to 1,000.
- The full source query and eligibility constraints have not yet been established.

**Required investigation**
- Inspect the source query, ordering, pagination, status filters, ownership filters, and permission boundary.
- Determine which Purchase Requirements should be selectable for a new Purchase Request.
- Verify behavior when many records exist and when no eligible records exist.

**Acceptance criteria**
- Eligibility rules match the approved business workflow.
- Selection does not expose ineligible or unauthorized records.
- Large result sets behave predictably and are not silently truncated in a way that breaks the workflow.

## Reconciliation Outcome — SUP-01 through SUP-07

**Reconciliation status:** Reconciled at the investigation and automated-verification level; browser verification remains outstanding for applicable items.

The SUP-01 through SUP-07 findings have been reviewed against the investigation evidence and the focused changes or dispositions recorded during this remediation cycle.

| Finding | Reconciled outcome |
|---|---|
| SUP-01 — Purchase Request status editing | Status is controlled by the application rather than ordinary form input. Focused form, route, and workflow regression tests passed. Browser confirmation remains pending. |
| SUP-02 — Purchase Request workflow actions | Permission-protected, POST-only workflow action routes and detail-page controls were implemented using the existing commands and permissions. Focused regression tests passed. Browser confirmation remains pending. |
| SUP-03 — Purchase Request route-test coverage | The focused route-test inventory found no obvious missing core-handler coverage gap. Closed on the evidence reviewed; this does not claim exhaustive branch or error-path coverage. |
| SUP-04 — Estimated cost fields | Approved explanatory text was added to clarify the purpose of the form and the optional estimated-cost fields. Focused form tests passed. Business rules were not changed, and automatic cost calculation was not introduced. |
| SUP-05 — Purchase Request action discoverability | List actions are displayed according to the existing create, update, and delete permissions. Focused route and permission-visibility tests passed. Browser confirmation remains pending. |
| SUP-06 — Catering-to-Procurement progression | The observed progression is consistent with the intended cross-module workflow. No defect was established; no code change was required. |
| SUP-07 — Purchase Requirement eligibility | Deferred because the applicable eligibility rules have not been established and no defect has been confirmed. No code change was made. |

### Verification and remaining boundaries

- Focused automated regression checks passed for the implemented SUP-01, SUP-02, SUP-04, and SUP-05 changes.
- Automated test results do not substitute for browser verification. The applicable Purchase Request creation, editing, workflow-action, and permission-sensitive list/detail journeys remain to be confirmed in the browser.
- SUP-03 and SUP-06 are closed only within the scope of the evidence reviewed. SUP-07 remains deferred pending clarification of the eligibility rules.
- This reconciliation does not mark the overall browser UAT or Gate 6 as complete. Existing controlled-data, authorization, backup/recovery, and reset/seed restrictions remain in force.
- No database changes, migrations, staging, or commits are authorized by this subsection. The authoritative browser UAT baseline, workflow rules register, and ICRC workshop documents retain their existing authority and purpose.

### SUP-08 — Reconcile the existing 39 uncommitted paths

**Classification:** Change-control and integration reconciliation
**Status:** Blocked pending inventory and explicit approval for any subsequent changes
**Priority:** Critical for change control

**Baseline evidence**
- The previously inspected Git status showed 17 modified tracked paths and 22 untracked paths.
- The changes span Catering requirements, inventory allocation/availability/fulfilment services, lifecycle transaction boundaries, related tests, two migration files, templates, and workshop/workflow documentation.
- The three workflow/workshop documents listed in Section 2 are untracked and must be preserved.
- The approved Browser UAT baseline describes earlier R01–R12 implementation and acceptance conditions; the current uncommitted paths require reconciliation against that history.

**Required investigation**
1. Reconfirm the current Git status without staging or modifying files.
2. Categorize each path by feature, purpose, dependencies, test coverage, and relationship to the approved baseline.
3. Inspect the relevant diffs and new files in small, focused batches.
4. Identify completed work, incomplete work, overlaps, migration dependencies, and documentation relationships.
5. Compare implementation claims with available test and browser evidence.
6. Propose a safe reconciliation plan before making any changes.

**Acceptance criteria**
- All existing paths are accounted for in a reconciliation inventory.
- Existing records and the three protected untracked documents are preserved.
- No unrelated changes are discarded or silently absorbed into a new commit.
- No migration or live-database mutation occurs without explicit authorization.
- Staging and committing occur only after a separate explicit approval.

## 5. Cross-cutting controls

The following controls apply to every supplemental finding:

1. **Architecture first:** verify module ownership, workflow rules, permissions, and service boundaries before proposing implementation.
2. **Evidence before conclusions:** distinguish directly observed behavior from assumptions and unverified coverage.
3. **No unauthorized code changes:** investigation does not authorize implementation.
4. **No live-data mutations:** preserve the current UAT dataset and existing ICRC scenario records.
5. **No unauthorized migrations:** inspect migration dependencies without applying them.
6. **Focused tests:** use isolated tests and controlled fixtures; do not connect test runs to or mutate the live UAT database.
7. **Controlled Git workflow:** do not stage, commit, reset, checkout, stash, or discard work without explicit approval.
8. **Documentation preservation:** update this register independently. Existing architecture, baseline, workflow, and workshop documents retain their respective authority.
9. **Gate 6 remains pending:** supplemental investigation or code completion alone does not establish browser acceptance or pilot readiness.

## 6. Closure protocol

A supplemental finding may be marked **Verified** only when its stated acceptance criteria have supporting test or browser evidence.

It may be marked **Closed** when:
- verification evidence is recorded;
- any overlap with UAT-R01–R12 is reconciled;
- required architecture or permission decisions are recorded in the appropriate authoritative document, with authorization;
- related tests pass; and
- any required Git checkpoint is separately approved and completed.

Closing a supplemental finding does not close an original baseline finding or establish Gate 6 acceptance unless the baseline's own acceptance requirements are satisfied.

## 7. Current register summary

| ID | Finding | Status | Priority |
|---|---|---|---|
| SUP-01 | Purchase Request status editable as ordinary form data | Confirmed; remediation not authorized | High |
| SUP-02 | Purchase Request workflow actions not evident in browser | Investigating | High |
| SUP-03 | Purchase Request route-test coverage inventory | Investigating | High |
| SUP-04 | Blank estimated cost fields | Investigating | Medium |
| SUP-05 | Purchase Request action discoverability | Investigating | Medium |
| SUP-06 | Catering-to-Procurement progression | Investigating | High |
| SUP-07 | Purchase Requirement eligibility filtering | Investigating | Medium |
| SUP-08 | Reconcile 39 uncommitted paths | Blocked pending inventory and approval | Critical |

**Acceptance position:** This register records supplemental investigations and change-control requirements. It does not alter the approved Browser UAT baseline, authorize implementation, authorize database preparation, or change the pending Gate 6 decision.
