const webhookBody = $('IQRA PDF Generation Webhook').item.json.body || {};
const table = webhookBody.table_name || '';
let slug = webhookBody.template_slug || '';
if (!slug) {
  const map = {
    'FRM-U2-001_Drawing_Issue_Register': 'drawing-issue-001',
    'FRM-U2-002_Document_Format_Procedure_Master_List': 'document-master-002',
    'FRM-U2-003_Calibration_Master_List': 'calibration-003',
    'FRM-U2-004_Readiness_Closure_Checklist': 'readiness-004',
    'FRM-U2-005_IMIR': 'imir-005',
    'FRM-U2-006_Traveller': 'traveller-006',
    'FRM-U2-007A_Cutting': 'cutting-007a',
    'FRM-U2-007B_Drilling_Parts': 'drilling-parts-007b',
    'FRM-U2-007C_Drilling_BuiltUp': 'drilling-builtup-007c',
    'FRM-U2-008A_Builtup_Fitup_SAW': 'fitup-saw-008a',
    'FRM-U2-008B_Attachment_Fitup_FCAW': 'fitup-fcaw-008b',
    'FRM-U2-012A_SAW_Welding': 'welding-saw-012a',
    'FRM-U2-012B_FCAW_Welding': 'welding-fcaw-012b',
    'FRM-U2-013_PT_DPT': 'pt-dpt-013',
    'FRM-U2-014_Repair_Closure': 'repair-014',
    'FRM-U2-015_Final_Release': 'final-release-015',
    'FRM-U2-016A_Blasting': 'blasting-016a',
    'FRM-U2-016B_Primer': 'primer-016b',
    'FRM-U2-016C_Final_Coat': 'final-coat-016c',
    'FRM-U2-017A_Marking_Packing': 'marking-packing-017a',
    'FRM-U2-017B_Dispatch_Clearance': 'dispatch-017b',
    'FRM-U2-018_Dossier_Index': 'dossier-index-018',
    'SE-013_Site_Receipt': 'site-receipt-013',
    // --- Phase 3: Unit I (FRM-U1-001..022) + Site Erection (SE-001..042, SE-013 above) ---
    'FRM-U1-001_Drawing_Issue_Register': 'frm-u1-001',  // FRM-U1-001
    'FRM-U1-002_Document_Format_Master_List': 'frm-u1-002',  // FRM-U1-002
    'FRM-U1-003_Procedure_and_WMS_Register': 'frm-u1-003',  // FRM-U1-003
    'FRM-U1-004_Work_Instruction_Register': 'frm-u1-004',  // FRM-U1-004
    'FRM-U1-005_Calibration_and_Tool_Master_List': 'frm-u1-005',  // FRM-U1-005
    'FRM-U1-006_Readiness_Closure_Checklist': 'frm-u1-006',  // FRM-U1-006
    'FRM-U1-007_Incoming_Material_Inspection_Secondaries_Rods_ERW': 'frm-u1-007',  // FRM-U1-007
    'FRM-U1-008_Incoming_Material_Inspection_Sheeting_Trim_Coils': 'frm-u1-008',  // FRM-U1-008
    'FRM-U1-009_Bought_out_Item_Receipt_and_Approval': 'frm-u1-009',  // FRM-U1-009
    'FRM-U1-010_Material_Traceability_Register_Traveller': 'frm-u1-010',  // FRM-U1-010
    'FRM-U1-011_Purlin_Girt_Eave_Strut_Rod_Line_Inspection_Report': 'frm-u1-011',  // FRM-U1-011
    'FRM-U1-012_Sheeting_Panel_Forming_Inspection_Report': 'frm-u1-012',  // FRM-U1-012
    'FRM-U1-013_Trim_Flashing_Gutter_Accessory_Forming_Inspection_Report': 'frm-u1-013',  // FRM-U1-013
    'FRM-U1-014_Fastener_Sealant_Closure_Lot_Control_Log': 'frm-u1-014',  // FRM-U1-014
    'FRM-U1-015_Insulation_Safety_Mesh_Inspection_Report': 'frm-u1-015',  // FRM-U1-015
    'FRM-U1-016_Polycarbonate_Skylight_Ventilator_Inspection_Report': 'frm-u1-016',  // FRM-U1-016
    'FRM-U1-017_Roof_Sheeting_Material_Handover_and_Accessory_Kit_Checklist': 'frm-u1-017',  // FRM-U1-017
    'FRM-U1-018_Finish_Integrity_and_Damage_Control_Log': 'frm-u1-018',  // FRM-U1-018
    'FRM-U1-019_Issue_Correction_and_Recheck_Log': 'frm-u1-019',  // FRM-U1-019
    'FRM-U1-020_Final_Unit_I_Release_Report': 'frm-u1-020',  // FRM-U1-020
    'FRM-U1-021_Packing_Dispatch_Clearance_Report': 'frm-u1-021',  // FRM-U1-021
    'FRM-U1-022_Dossier_Index': 'frm-u1-022',  // FRM-U1-022
    'SE-001_Drawing_Issue_Register_Site_Erection': 'se-001',  // SE-001
    'SE-002_Format_Register_Site_Erection': 'se-002',  // SE-002
    'SE-003_Procedure_and_WMS_Register_Site_Erection': 'se-003',  // SE-003
    'SE-004_Work_Instruction_Register_Site_Erection': 'se-004',  // SE-004
    'SE-005_Contractor_Provider_Review_and_Acceptance_Register': 'se-005',  // SE-005
    'SE-006_Site_Start_Checklist': 'se-006',  // SE-006
    'SE-007_Contractor_Mobilisation_and_Responsibility_Matrix_Record': 'se-007',  // SE-007
    'SE-008_Contractor_Manpower_Deployment_and_Competency_Record': 'se-008',  // SE-008
    'SE-009_Contractor_Equipment_Tool_Tackle_Register': 'se-009',  // SE-009
    'SE-010_Crane_Deployment_and_Certificate_Record': 'se-010',  // SE-010
    'SE-011_Survey_Instrument_Torque_Wrench_Paint_Check_Measuring_Tool_Record': 'se-011',  // SE-011 (spec name)
    'SE-011_Survey_Instrument_Torque_Wrench_Paint_Check_Measuring_Tool_R': 'se-011',  // SE-011 LIVE truncated table name (Airtable cut at 66 chars) — fixes I-12 routing miss
    'SE-012_Lifting_Gear_Rigging_Gear_Inspection_Record': 'se-012',  // SE-012
    'SE-014_Unloading_Storage_and_Identification_Control_Record': 'se-014',  // SE-014
    'SE-015_Civil_Interface_Pedestal_Anchor_Bolt_Check_Record': 'se-015',  // SE-015
    'SE-016_Pre_Erection_Survey_and_Reference_Check_Record': 'se-016',  // SE-016
    'SE-017_Column_Erection_Inspection_Report': 'se-017',  // SE-017
    'SE-018_Rafter_Beam_Erection_Inspection_Report': 'se-018',  // SE-018
    'SE-019_Bracing_Sag_Rod_Tie_Member_Inspection_Report': 'se-019',  // SE-019
    'SE-020_Secondary_Member_Erection_Inspection_Report': 'se-020',  // SE-020
    'SE-021_Alignment_Line_Level_Plumb_Bay_Geometry_Report': 'se-021',  // SE-021
    'SE-022_Temporary_Stability_and_Erection_Sequence_Check_Record': 'se-022',  // SE-022
    'SE-023_Bolt_Issue_and_Bolt_Identification_Record': 'se-023',  // SE-023
    'SE-024_Snug_Tightening_Inspection_Record': 'se-024',  // SE-024
    'SE-025_Final_Torque_Turn_of_Nut_Verification_Record': 'se-025',  // SE-025
    'SE-026_Bolt_Replacement_Recheck_Record': 'se-026',  // SE-026
    'SE-027_Roof_Sheeting_Installation_Inspection_Report': 'se-027',  // SE-027
    'SE-028_Wall_Cladding_Installation_Inspection_Report': 'se-028',  // SE-028
    'SE-029_Insulation_Safety_Mesh_Roof_Accessory_Inspection_Report': 'se-029',  // SE-029
    'SE-030_Skylight_Polycarbonate_Ventilator_Installation_Record': 'se-030',  // SE-030
    'SE-031_Ridge_Flashing_Gutter_Downspout_Trim_Inspection_Record': 'se-031',  // SE-031
    'SE-032_Sheeting_Fastener_and_Sealant_Inspection_Record': 'se-032',  // SE-032
    'SE-033_NSPL_Site_Touch_up_Painting_Inspection_Record': 'se-033',  // SE-033
    'SE-034_Site_Issue_Correction_Recheck_Log': 'se-034',  // SE-034
    'SE-035_Punch_Point_Register': 'se-035',  // SE-035
    'SE-036_Punch_Point_Clearance_Record': 'se-036',  // SE-036
    'SE-037_Final_Site_Release_Handover_Inspection_Report': 'se-037',  // SE-037
    'SE-038_Site_Dossier_Index': 'se-038',  // SE-038
    'SE-039_Daily_Erection_Progress_and_Inspection_Summary': 'se-039',  // SE-039
    'SE-040_NSPL_Issue_Cover_Sheet_to_IQRA_for_Final_Review': 'se-040',  // SE-040
    'SE-041_Site_Affected_Member_Coating_and_Finish_Restoration_Record': 'se-041',  // SE-041
    'SE-042_Touch_up_Paint_Material_Batch_Area_DFT_Log': 'se-042',  // SE-042
  };
  slug = map[table] || '';
  // ponytail: Airtable truncates long table names (SE-011 was cut at 66 chars → routing miss, I-12).
  // If exact match fails, match by prefix: a truncated live name is a strict prefix of the full spec key.
  // Guard len>20 so short codes can't false-match. Upgrade path: send template_slug in the webhook body.
  if (!slug && table.length > 20) {
    const k = Object.keys(map).find(key => key.startsWith(table));
    if (k) slug = map[k];
  }
}
if (!slug) {
  return { json: { table_name: table, record_id: webhookBody.record_id, template_slug: '', error: 'No template mapped for table ' + table, skip: true } };
}
return { json: { table_name: table, record_id: webhookBody.record_id, template_slug: slug, template_url: 'https://sandy-zippy.github.io/iqra-pdf-templates/' + slug + '.html', skip: false } };