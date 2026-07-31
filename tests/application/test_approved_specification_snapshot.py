from __future__ import annotations
from dataclasses import dataclass, replace
import pytest
from src.application.approved_specification_read_model import ApprovedSpecificationReadModel
from src.application.approved_specification_snapshot_service import ApprovedSpecificationSnapshotError, ApprovedSpecificationSnapshotService
from src.application.specification_review_service import ReviewableField
from src.domain.specification_review import ReviewStatus, SnapshotEligibilityResult
from src.persistence.approved_specification_repository import ApprovedSpecificationPersistenceError

@dataclass(frozen=True)
class Candidate:
    original_value: object
    mandatory: bool
    status: ReviewStatus
    corrected_value: object|None=None
@dataclass(frozen=True)
class Comparison:
    field_key: str
    existing_value: object
    candidate: Candidate
@dataclass(frozen=True)
class Baseline:
    confirmed: bool=True
@dataclass(frozen=True)
class State:
    project_id:str='project-1'; existing_dataset_id:str='existing'; proposed_dataset_id:str='proposed'; comparisons:tuple=(); existing_baseline:object=Baseline(); has_unresolved_validation_issue:bool=False; eligibility:object=SnapshotEligibilityResult(True,())
@dataclass(frozen=True)
class Review:
    review_revision_id:str='revision-3'; review_id:str='review-1'; revision_number:int=3; state:State=State()
class ReviewRepo:
    def __init__(self, review): self.review=review
    def get_latest(self, review_id, *, project_id):
        if review_id!='review-1': raise KeyError(review_id)
        if project_id!='project-1': raise Exception('bad scope')
        return self.review
class DatasetRepo:
    def __init__(self):
        self.rows={'existing':{'project_id':'project-1','validation_status':'valid','canonical_json':{'gsm':120,'caliper':1.0,'flute':'B','coating':None}},'proposed':{'project_id':'project-1','validation_status':'valid','canonical_json':{'gsm':140,'caliper':0.8,'flute':'B','coating':None}}}
    def get(self, dataset_id): return self.rows[dataset_id]
class SnapshotRepo:
    def __init__(self): self.snapshot=None; self.created=0
    def get_for_review(self, review_id, *, project_id): return self.snapshot
    def create(self,snapshot): self.created+=1; self.snapshot=snapshot; return snapshot
    def get(self,snapshot_id,*,project_id):
        if self.snapshot and self.snapshot.snapshot_id==snapshot_id and self.snapshot.project_id==project_id:return self.snapshot
        raise ApprovedSpecificationPersistenceError('snapshot_not_found','not found')
    def list_for_project(self,project_id): return [] if self.snapshot is None else [self.snapshot]

def fields():
 return (ReviewableField('caliper',('caliper',)),ReviewableField('coating',('coating',),mandatory=False),ReviewableField('flute',('flute',)),ReviewableField('gsm',('gsm',)))
def review():
 return Review(state=State(comparisons=(Comparison('gsm',120,Candidate(140,True,ReviewStatus.ACCEPTED)),Comparison('caliper',1.0,Candidate(0.8,True,ReviewStatus.CORRECTED,0.9)))))
def service(r=None,s=None,d=None):
 return ApprovedSpecificationSnapshotService(r or ReviewRepo(review()),s or SnapshotRepo(),d or DatasetRepo())
def create(svc,**changes):
 args=dict(project_id='project-1',review_id='review-1',source_review_revision_id='revision-3',actor_reference='buyer@example.com',approval_reason='Reviewed packaging specification.',fields=fields(),optional_exclusions=('coating',));args.update(changes);return svc.create_snapshot(**args)

def test_materializes_accepted_corrected_unchanged_and_optional_exclusion():
 snap=create(service()); values={v.field_key:(v.value,v.source) for v in snap.approved_values}; assert values=={'caliper':(0.9,'corrected'),'flute':('B','unchanged'),'gsm':(140,'accepted_proposed')}; assert snap.excluded_fields==('coating',)
def test_rejected_value_retains_existing():
 r=review(); r=replace(r,state=replace(r.state,comparisons=(Comparison('gsm',120,Candidate(140,True,ReviewStatus.REJECTED)),Comparison('caliper',1.0,Candidate(0.8,True,ReviewStatus.CORRECTED,0.9))))); snap=create(service(r=ReviewRepo(r))); assert {v.field_key:v.value for v in snap.approved_values}['gsm']==120
def test_historical_revision_is_rejected():
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(),source_review_revision_id='revision-2');assert e.value.code=='historical_revision'
def test_empty_project_is_rejected():
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(),project_id=' ');assert e.value.code=='project_required'
def test_empty_actor_is_rejected():
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(),actor_reference=' ');assert e.value.code=='actor_required'
def test_empty_reason_is_rejected():
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(),approval_reason=' ');assert e.value.code=='approval_reason_required'
def test_recomputed_ineligible_state_is_rejected():
 r=review();r=replace(r,state=replace(r.state,existing_baseline=Baseline(False),eligibility=SnapshotEligibilityResult(False,('existing_baseline_not_confirmed',))));
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(r=ReviewRepo(r)));assert e.value.code=='review_not_eligible'
def test_stored_eligibility_mismatch_fails_closed():
 r=review();r=replace(r,state=replace(r.state,eligibility=SnapshotEligibilityResult(False,('x',))));
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(r=ReviewRepo(r)));assert e.value.code=='review_integrity_error'
def test_mandatory_field_cannot_be_excluded():
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(),optional_exclusions=('gsm',));assert e.value.code=='invalid_optional_exclusion'
def test_identical_retry_returns_existing_without_second_create():
 repo=SnapshotRepo();svc=service(s=repo);first=create(svc);second=create(svc);assert second is first;assert repo.created==1
def test_conflicting_retry_fails_closed():
 repo=SnapshotRepo();svc=service(s=repo);create(svc)
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(svc,actor_reference='other');assert e.value.code=='conflicting_snapshot'
def test_source_dataset_mismatch_fails_closed():
 d=DatasetRepo();d.rows['proposed']['canonical_json']['gsm']=150
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:create(service(d=d));assert e.value.code=='review_source_mismatch'
def test_read_model_translates_project_scoped_repository_errors():
 rm=ApprovedSpecificationReadModel(SnapshotRepo())
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:rm.get_snapshot('missing',project_id='project-1');assert e.value.code=='snapshot_not_found'
def test_read_model_requires_project_scope():
 rm=ApprovedSpecificationReadModel(SnapshotRepo())
 with pytest.raises(ApprovedSpecificationSnapshotError) as e:rm.list_snapshots_for_project(' ');assert e.value.code=='project_required'
def test_read_model_returns_project_snapshot():
 repo=SnapshotRepo();snap=create(service(s=repo));rm=ApprovedSpecificationReadModel(repo);assert rm.get_snapshot(snap.snapshot_id,project_id='project-1')==snap
