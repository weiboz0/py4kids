# Borrowed-tools fixture shapes

These synthetic fixtures mirror exactly the three notebook shapes governed by design 004.

1. `given-pair/` is an exercise plus paired solution with a byte-identical GIVEN region and shared `py4kids_task_id`.
2. `lesson-real-form/` is a lesson `no-exec` plus `real-form` code cell.
3. `markdown-real-form/` is a solution `real-form` markdown Python fence.

Their manifests are schema-v2 unit declarations used by the mutation tests.
