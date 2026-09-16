# Tranche 0 local acceptance

- observed_at_utc: 2026-09-16T05:20:46.208237+00:00
- endpoint: `http://127.0.0.1:8080/v1`
- provider_id: `local-llama`
- model_id: `/Users/knowurknot/Downloads/Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q4_K_M.gguf`
- provider_max_concurrent_requests: `1`
- credential: none

## One seat
- run_id: `run_6ffefcf47f074f29a9aad9d4bb5e6e60`
- terminal_state: `completed`
- output: `ONE_OK`

## Six seats through provider scheduler
- run_ids: `["run_fd76a7dec8b64069adfde7d6550db4bb", "run_bbe85492e7de462f8b906dd4035ba3c9", "run_7c09df32db5c442cbd49aa220914e471", "run_13e38030d5c3418b8d667196e4df7a00", "run_d04ad30618af418c93990dd8b3d1ba89", "run_28dc777d9c98412d88387fbfe1873dd1"]`
- terminal_states: `["completed", "completed", "completed", "completed", "completed", "completed"]`
- outputs: `["SIX_OK", "SIX_OK", "SIX_OK", "SIX_OK", "SIX_OK", "SIX_OK"]`

## Cancel in flight
- run_id: `run_c76f44cf12f04ae19f7b16341e67bd90`
- terminal_state: `cancelled_by_user`
- partial_output_sha256: `6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b`
- partial_chunk_count: `1`

## Invalid provider beside successful local seat
- good_run_id: `run_87ef06df610343a4a62fe0fd5ff4c6a8`
- good_terminal_state: `completed`
- good_output: `MIXED_OK`
- invalid_run_id: `run_66a4f78d837d4c478124277bad10fed4`
- invalid_terminal_state: `failed`
- invalid_failure_class: `provider_unavailable`
