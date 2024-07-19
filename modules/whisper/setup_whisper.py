import os
import base64
import subprocess

folder_path = f'modules/whisper'

file_data = [
    ('whisper_module.py', 'aW1wb3J0IGJhc2U2NAppbXBvcnQgZmZtcGVnCgpmcm9tIG1vZHVsZXMuYmFzZV9tb2R1bGUgaW1wb3J0IEJhc2VNb2R1bGUKZnJvbSBtb2R1bGVzLndoaXNwZXIud2hpc3BlciBpbXBvcnQgcnVuX3doaXNwZXIKZnJvbSBtb2R1bGVzLndoaXNwZXIuY29udmVydF9maWxlIGltcG9ydCBjb252ZXJ0X3RvX3dhdgpmcm9tIG1vZHVsZXMud2hpc3Blci5zZXR1cC5hdWRpb19tYW5hZ2VyIGltcG9ydCBBdWRpb01hbmFnZXIKCgpjbGFzcyBXaGlzcGVyTW9kdWxlKEJhc2VNb2R1bGUpOgogICAgZGVmIF9faW5pdF9fKHNlbGYpOgogICAgICAgIHN1cGVyKCkuX19pbml0X18oKQogICAgICAgIHNlbGYuYXVkaW8gPSBBdWRpb01hbmFnZXIoKQogICAgICAgIAogICAgYXN5bmMgZGVmIHByb2Nlc3Moc2VsZiwgYmFzZTY0X3JlcXVlc3Q6IHN0cikgLT4gc3RyOgogICAgICAgIHNlbGYuYXVkaW8uc2F2ZV9hdWRpbyhiYXNlNjRfcmVxdWVzdCkKICAgICAgICBjb252ZXJ0X3RvX3dhdigibW9kdWxlX3JlZ2lzdHJhci9tb2R1bGVzL3doaXNwZXIvaW4vaW5wdXQud2F2IikKICAgICAgICBydW5fd2hpc3BlcigKICAgICAgICAgICAgd2hpc3Blcl9iaW49Im1vZHVsZV9yZWdpc3RyYXIvbW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwL21haW4iLAogICAgICAgICAgICBmaWxlX3BhdGg9Im1vZHVsZV9yZWdpc3RyYXIvbW9kdWxlcy93aGlzcGVyL291dC9vdXRwdXQud2F2IiwKICAgICAgICAgICAgbW9kZWxfcGF0aD0ibW9kdWxlX3JlZ2lzdHJhci9tb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAvbW9kZWxzL2dnbWwtYmFzZS5lbi5iaW4iCiAgICAgICAgKQogICAgICAgIGRhdGEgPSBzZWxmLmF1ZGlvLnJldHJpZXZlX3Byb2Nlc3NlZF9kYXRhKCkKICAgICAgICByZXR1cm4gc2VsZi5hdWRpby5lbmNvZGVfcHJvY2Vzc2VkX2RhdGEoZGF0YSkKICAgICAgICAKICAgICAgICA='),
    ('example.sh', 'IyEgL2Jpbi9iYXNoCgpjcCBtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAvc2FtcGxlcy9qZmsud2F2IG1vZHVsZXMvd2hpc3Blci9pbgoKcHl0aG9uIG1vZHVsZXMvd2hpc3Blci9jb252ZXJ0X2ZpbGUucHkgLWYgbW9kdWxlcy93aGlzcGVyL2luL2pmay53YXYKCnB5dGhvbiBtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5weSAtZiBtb2R1bGVzL3doaXNwZXIvaW4vamZrLndhdiAtbSBtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAvbW9kZWxzL2dnbWwtYmFzZS5lbi5iaW4gLXcgbW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwL21haW4K'),
    ('install_whisper.py', 'aW1wb3J0IG9zCmltcG9ydCBzdWJwcm9jZXNzCmltcG9ydCBqc29uCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKc3VicHJvY2Vzcy5ydW4oWyJwaXAiLCAiaW5zdGFsbCIsICJsb2d1cnUiXSwgY2hlY2s9VHJ1ZSkKCmZyb20gbG9ndXJ1IGltcG9ydCBsb2dnZXIKCgpkZWYgaW5zdGFsbF9jdWRhKCk6CiAgICBjb21tYW5kcyA9ICIiIgojIS9iaW4vYmFzaAojIEluc3RhbGwgQ1VEQQpwaXAgaW5zdGFsbCBudmlkaWEtcHlpbmRleAp3Z2V0IGh0dHBzOi8vZGV2ZWxvcGVyLmRvd25sb2FkLm52aWRpYS5jb20vY29tcHV0ZS9jdWRhL3JlcG9zL3VidW50dTIyMDQveDg2XzY0L2N1ZGEtdWJ1bnR1MjIwNC5waW4Kc3VkbyBtdiBjdWRhLXVidW50dTIyMDQucGluIC9ldGMvYXB0L3ByZWZlcmVuY2VzLmQvY3VkYS1yZXBvc2l0b3J5LXBpbi02MDAKd2dldCBodHRwczovL2RldmVsb3Blci5kb3dubG9hZC5udmlkaWEuY29tL2NvbXB1dGUvY3VkYS8xMi4zLjAvbG9jYWxfaW5zdGFsbGVycy9jdWRhLXJlcG8tdWJ1bnR1MjIwNC0xMi0zLWxvY2FsXzEyLjMuMC01NDUuMjMuMDYtMV9hbWQ2NC5kZWIKc3VkbyBkcGtnIC1pIGN1ZGEtcmVwby11YnVudHUyMjA0LTEyLTMtbG9jYWxfMTIuMy4wLTU0NS4yMy4wNi0xX2FtZDY0LmRlYgpzdWRvIGNwIC92YXIvY3VkYS1yZXBvLXVidW50dTIyMDQtMTItMy1sb2NhbC9jdWRhLSota2V5cmluZy5ncGcgL3Vzci9zaGFyZS9rZXlyaW5ncy8Kc3VkbyBhcHQtZ2V0IHVwZGF0ZQpzdWRvIGFwdC1nZXQgLXkgaW5zdGFsbCBjdWRhLXRvb2xraXQtMTItMwoiIiIKICAgIGN1ZGEgPSBpbnB1dCgiRG8geW91IHdhbnQgdG8gaW5zdGFsbCBDVURBIDEyLjM/ICh5L24pOiAiKQogICAgY3VkYSA9IGN1ZGEgaW4gWyJ5IiwgIlkiLCAieWVzIiwgIlllcyJdCiAgICBpZiBjdWRhOgogICAgICAgIHN1YnByb2Nlc3MucnVuKFtjb21tYW5kc10sIGNoZWNrPVRydWUsIHNoZWxsPVRydWUpCiAgICByZXR1cm4gY3VkYQoKCmluc3RhbGxfY3VkYSgpCgppbnN0YWxsX3doaXNwZXJfc2ggPSAiIiIjIS9iaW4vYmFzaAoKIyBJbnN0YWxsIHdoaXNwZXIuY3BwCmdpdCBjbG9uZSBodHRwczovL2dpdGh1Yi5jb20vZ2dlcmdhbm92L3doaXNwZXIuY3BwLmdpdCBtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAKY2QgbW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwCm1ha2UgY2xlYW4KV0hJU1BFUl9DQkxBU1Q9MSBtYWtlIC1qCgojIERvd25sb2FkIFdoaXNwZXIgbW9kZWwKYmFzaCBtb2RlbHMvZG93bmxvYWQtZ2dtbC1tb2RlbC5zaCBiYXNlLmVuCiAgICAKIyBNYWtlIGluIGFuZCBvdXQgZGlycwpjZCAuLiAKbWtkaXIgLXAgaW4gb3V0CgpjZCAuLi8uLi8uLgoKIyBSdW4gZXhhbXBsZQpiYXNoIG1vZHVsZXMvd2hpc3Blci9leGFtcGxlLnNoCiIiIgpleGFtcGxlX3NoID0gIiIiIyEgL2Jpbi9iYXNoCgpjcCBtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAvc2FtcGxlcy9qZmsud2F2IG1vZHVsZXMvd2hpc3Blci9pbgoKcHl0aG9uIG1vZHVsZXMvd2hpc3Blci9jb252ZXJ0X2ZpbGUucHkgLWYgbW9kdWxlcy93aGlzcGVyL2luL2pmay53YXYKCnB5dGhvbiBtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5weSAtZiBtb2R1bGVzL3doaXNwZXIvaW4vamZrLndhdiAtbSBtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAvbW9kZWxzL2dnbWwtYmFzZS5lbi5iaW4gLXcgbW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwL21haW4KIiIiCgpjb252ZXJ0X2ZpbGVfcHkgPSAiIiJpbXBvcnQgYXJncGFyc2UKaW1wb3J0IHN1YnByb2Nlc3MKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCgoKCmRlZiBjb252ZXJ0X3RvX3dhdihmaWxlX3BhdGgpOgogICAgaW5wdXRfbmFtZSA9IFBhdGgoZmlsZV9wYXRoKQogICAgb3V0cHV0X25hbWUgPSBpbnB1dF9uYW1lLm5hbWUuZm9ybWF0KCJ3YXYiKQogICAgb3V0cHV0X3BhdGggPSBQYXRoKGYibW9kdWxlcy93aGlzcGVyL291dC97b3V0cHV0X25hbWV9IikKICAgIHN1YnByb2Nlc3MucnVuKAogICAgICAgIFsKICAgICAgICAgICAgImZmbXBlZyIsCiAgICAgICAgICAgICItaSIsCiAgICAgICAgICAgIGYie2lucHV0X25hbWV9IiwKICAgICAgICAgICAgIi1hciIsCiAgICAgICAgICAgICIxNjAwMCIsCiAgICAgICAgICAgICItYWMiLAogICAgICAgICAgICAiMSIsCiAgICAgICAgICAgICItYzphIiwKICAgICAgICAgICAgInBjbV9zMTZsZSIsCiAgICAgICAgICAgIGYie291dHB1dF9wYXRofSIsCiAgICAgICAgXSwKICAgICAgICBjaGVjaz1UcnVlLAogICAgKQoKCmRlZiBwYXJzZV9hcmdzKCk6CiAgICBwYXJzZXIgPSBhcmdwYXJzZS5Bcmd1bWVudFBhcnNlcigpCiAgICBwYXJzZXIuYWRkX2FyZ3VtZW50KCItZiIsICItLWZpbGVfcGF0aCIsIHR5cGU9c3RyLCByZXF1aXJlZD1UcnVlKQogICAgYXJncyA9IHBhcnNlci5wYXJzZV9hcmdzKCkKICAgIHJldHVybiBhcmdzCgoKaWYgX19uYW1lX18gPT0gIl9fbWFpbl9fIjoKICAgIGZpbGVfcGF0aCA9IHBhcnNlX2FyZ3MoKS5maWxlX3BhdGgKICAgIGNvbnZlcnRfdG9fd2F2KGZpbGVfcGF0aCkKIiIiCgp3aGlzcGVyX3B5ID0gIiIiaW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBzdWJwcm9jZXNzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKZnJvbSBsb2d1cnUgaW1wb3J0IGxvZ2dlcgoKZGVmIHJ1bl93aGlzcGVyKAogICAgd2hpc3Blcl9iaW49Im1vZHVsZXMvd2hpc3Blci93aGlzcGVyLmNwcC9tYWluIiwKICAgIGZpbGVfcGF0aD0ibW9kdWxlcy93aGlzcGVyL2luL2pmay53YXYiLAogICAgbW9kZWxfcGF0aD0ibW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwL21vZGVscy9nZ21sLWJhc2UuZW4uYmluIiwKKToKICAgIGZpbGVfcGF0aCA9IFBhdGgoZmlsZV9wYXRoKQogICAgbW9kZWxfcGF0aCA9IFBhdGgobW9kZWxfcGF0aCkKICAgIHdoaXNwZXJfcGF0aCA9IFBhdGgod2hpc3Blcl9iaW4pCiAgICB0cnk6CiAgICAgICAgcmVzdWx0ID0gc3VicHJvY2Vzcy5ydW4oCiAgICAgICAgICAgIFtmInt3aGlzcGVyX2Jpbn0iLCAiLW0iLCBmInttb2RlbF9wYXRofSIsICItZiIsIGYie2ZpbGVfcGF0aH0iXSwKICAgICAgICAgICAgc3Rkb3V0PXN1YnByb2Nlc3MuUElQRSwKICAgICAgICAgICAgc3RkZXJyPXN1YnByb2Nlc3MuUElQRSwKICAgICAgICAgICAgY2hlY2s9VHJ1ZSwKICAgICAgICApCiAgICAgICAgbG9nZ2VyLmRlYnVnKHJlc3VsdC5zdGRvdXQuZGVjb2RlKCJ1dGYtOCIpKQogICAgICAgIHJldHVybiByZXN1bHQuc3Rkb3V0LmRlY29kZSgidXRmLTgiKQogICAgZXhjZXB0IHN1YnByb2Nlc3MuQ2FsbGVkUHJvY2Vzc0Vycm9yIGFzIGVycm9yOgogICAgICAgIGxvZ2dlci5lcnJvcihlcnJvcikKICAgICAgICByZXR1cm4gZXJyb3IKICAgIGV4Y2VwdCBSdW50aW1lRXJyb3IgYXMgZXJyb3I6CiAgICAgICAgbG9nZ2VyLmVycm9yKGVycm9yKQogICAgICAgIHJldHVybiBlcnJvcgoKCmRlZiBwYXJzZV9hcmdzKCk6CiAgICBwYXJzZXIgPSBhcmdwYXJzZS5Bcmd1bWVudFBhcnNlcigpCiAgICBwYXJzZXIuYWRkX2FyZ3VtZW50KAogICAgICAgICItZiIsICItLWZpbGVfcGF0aCIsIGRlZmF1bHQ9Im1vZHVsZXMvd2hpc3Blci9pbnB1dC9qZmsud2F2IiwgdHlwZT1zdHIsIHJlcXVpcmVkPUZhbHNlCiAgICApCiAgICBwYXJzZXIuYWRkX2FyZ3VtZW50KAogICAgICAgICItbSIsCiAgICAgICAgIi0tbW9kZWxfcGF0aCIsCiAgICAgICAgZGVmYXVsdD0ibW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwL21vZGVscy9nZ21sLWJhc2UuZW4uYmluIiwKICAgICAgICB0eXBlPXN0ciwKICAgICAgICByZXF1aXJlZD1GYWxzZSwKICAgICkKICAgIHBhcnNlci5hZGRfYXJndW1lbnQoIi13IiwgIi0td2hpc3Blcl9iaW4iLCBkZWZhdWx0PSJtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAvbWFpbiIsIHR5cGU9c3RyKQogICAgYXJncyA9IHBhcnNlci5wYXJzZV9hcmdzKCkKICAgIHJldHVybiBhcmdzCgoKaWYgX19uYW1lX18gPT0gIl9fbWFpbl9fIjoKICAgIGFyZ3MgPSBwYXJzZV9hcmdzKCkKICAgIHJ1bl93aGlzcGVyKCoqdmFycyhhcmdzKSkKIiIiCgppbmZlcmVuY2VfdHlwZXMgPSBQYXRoKCJtb2R1bGVzL2luZmVyZW5jZV90eXBlcy5qc29uIikKCnR5cGVfZGF0YSA9ICJ3aGlzcGVyIgpqc29uX2RhdGEgPSB7InR5cGUiOiBbXX0KaWYgb3MucGF0aC5leGlzdHMoaW5mZXJlbmNlX3R5cGVzKToKICAgIGpzb25fZGF0YSA9IGpzb24ubG9hZHMoaW5mZXJlbmNlX3R5cGVzLnJlYWRfdGV4dCgpKQpqc29uX2RhdGFbInR5cGUiXS5hcHBlbmQodHlwZV9kYXRhKQppbmZlcmVuY2VfdHlwZXMud3JpdGVfdGV4dChqc29uLmR1bXBzKGpzb25fZGF0YSkpCgoKZmlsZV9wYXRocyA9IHsKICAgICJpbnN0YWxsX3doaXNwZXJfc2giOiBQYXRoKAogICAgICAgICJtb2R1bGVzL3doaXNwZXIvaW5zdGFsbF93aGlzcGVyLnNoIgogICAgKSwKICAgICJleGFtcGxlX3NoIjogUGF0aCgibW9kdWxlcy93aGlzcGVyL2V4YW1wbGUuc2giKSwKICAgICJjb252ZXJ0X2ZpbGVfcHkiOiBQYXRoKCJtb2R1bGVzL3doaXNwZXIvY29udmVydF9maWxlLnB5IiksCiAgICAid2hpc3Blcl9weSI6IFBhdGgoIm1vZHVsZXMvd2hpc3Blci93aGlzcGVyLnB5IiksCn0KZGF0YSA9IHsKICAgICJpbnN0YWxsX3doaXNwZXJfc2giOiBpbnN0YWxsX3doaXNwZXJfc2gsCiAgICAiZXhhbXBsZV9zaCI6IGV4YW1wbGVfc2gsCiAgICAiY29udmVydF9maWxlX3B5IjogY29udmVydF9maWxlX3B5LAogICAgIndoaXNwZXJfcHkiOiB3aGlzcGVyX3B5LAp9CgoKZGVmIHdyaXRlX2ZpbGUoZmlsZV9kYXRhOiBzdHIsIGZpbGVfcGF0aDogc3RyKSAtPiBOb25lOgogICAgbG9nZ2VyLmRlYnVnKGYiXFxuZmlsZV9kYXRhOiB7ZmlsZV9kYXRhfVxcbmZpbGVfcGF0aDoge2ZpbGVfcGF0aH1cXG4iKQogICAgZmlsZV9wYXRoLndyaXRlX3RleHQoZmlsZV9kYXRhKQogICAgZmlsZV9wYXRoLmNobW9kKDBvNzc3KQoKCmZvciBrZXkgaW4gZmlsZV9wYXRocy5rZXlzKCk6CiAgICB3cml0ZV9maWxlKGRhdGFba2V5XSwgZmlsZV9wYXRoc1trZXldKQogICAgbG9nZ2VyLmRlYnVnKGYiXFxuZmlsZToge2ZpbGVfcGF0aHNba2V5XX1cXG4iKQoKc3VicHJvY2Vzcy5ydW4oCiAgICBbImJhc2giLCAibW9kdWxlcy93aGlzcGVyL2luc3RhbGxfd2hpc3Blci5zaCJdLCBjaGVjaz1UcnVlCikK'),
    ('install_whisper.sh', 'IyEvYmluL2Jhc2gKCiMgSW5zdGFsbCB3aGlzcGVyLmNwcApnaXQgY2xvbmUgaHR0cHM6Ly9naXRodWIuY29tL2dnZXJnYW5vdi93aGlzcGVyLmNwcC5naXQgbW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwCmNkIG1vZHVsZXMvd2hpc3Blci93aGlzcGVyLmNwcAptYWtlIGNsZWFuCldISVNQRVJfQ0JMQVNUPTEgbWFrZSAtagoKIyBEb3dubG9hZCBXaGlzcGVyIG1vZGVsCmJhc2ggbW9kZWxzL2Rvd25sb2FkLWdnbWwtbW9kZWwuc2ggYmFzZS5lbgogICAgCiMgTWFrZSBpbiBhbmQgb3V0IGRpcnMKY2QgLi4gCm1rZGlyIC1wIGluIG91dAoKY2QgLi4vLi4vLi4KCiMgUnVuIGV4YW1wbGUKYmFzaCBtb2R1bGVzL3doaXNwZXIvZXhhbXBsZS5zaAo='),
    ('audio_manager.py', 'aW1wb3J0IGJhc2U2NAppbXBvcnQgb3MKaW1wb3J0IHdhdmUKCgpjbGFzcyBBdWRpb01hbmFnZXI6CiAgICBkZWYgX19pbml0X18oc2VsZik6CiAgICAgICAgc2VsZi5pbnB1dF9wYXRoID0gIm1vZHVsZXMvd2hpc3Blci9pbi9hdWRpb19yZXF1ZXN0LndhdiIKICAgICAgICBzZWxmLm91dHB1dF9wYXRoID0gIm1vZHVsZXMvd2hpc3Blci9vdXQvYXVkaW9fcmVxdWVzdC53YXYiCgogICAgZGVmIGVuY29kZV9hdWRpbyhzZWxmLCBhdWRpb19wYXRoKToKICAgICAgICAiIiJFbmNvZGUgYXVkaW8gZmlsZSB0byBiYXNlNjQgc3RyaW5nLiIiIgogICAgICAgIHdpdGggb3BlbihhdWRpb19wYXRoLCAicmIiKSBhcyBhdWRpb19maWxlOgogICAgICAgICAgICBhdWRpb19jb250ZW50ID0gYXVkaW9fZmlsZS5yZWFkKCkKICAgICAgICByZXR1cm4gc2VsZi5lbmNvZGVfcHJvY2Vzc2VkX2RhdGEoYXVkaW9fY29udGVudCkKICAgIAogICAgZGVmIGRlY29kZV9hdWRpbyhzZWxmLCBiYXNlNjRfc3RyaW5nKToKICAgICAgICAiIiJEZWNvZGUgYmFzZTY0IHN0cmluZyB0byBhdWRpbyBkYXRhLiIiIgogICAgICAgIHJldHVybiBzZWxmLmRlY29kZV9wcm9jZXNzZWRfZGF0YShiYXNlNjRfc3RyaW5nKQoKICAgIGRlZiBzYXZlX2F1ZGlvKHNlbGYsIGJhc2U2NF9zdHJpbmcpOgogICAgICAgICIiIkRlY29kZSBhbmQgc2F2ZSBiYXNlNjQgYXVkaW8gc3RyaW5nIHRvIGlucHV0IHBhdGguIiIiCiAgICAgICAgYXVkaW9fZGF0YSA9IHNlbGYuZGVjb2RlX2F1ZGlvKGJhc2U2NF9zdHJpbmcpCiAgICAgICAgb3MubWFrZWRpcnMob3MucGF0aC5kaXJuYW1lKHNlbGYuaW5wdXRfcGF0aCksIGV4aXN0X29rPVRydWUpCiAgICAgICAgd2F2ZV9maWxlID0gd2F2ZS5vcGVuKHNlbGYuaW5wdXRfcGF0aCwgJ3diJykKICAgICAgICB3YXZlX2ZpbGUuc2V0bmNoYW5uZWxzKDEpCiAgICAgICAgd2F2ZV9maWxlLnNldHNhbXB3aWR0aCgyKSAgIyAxNi1iaXQKICAgICAgICB3YXZlX2ZpbGUuc2V0ZnJhbWVyYXRlKDE2MDAwKSAgIyAxNmtIegogICAgICAgIHdhdmVfZmlsZS53cml0ZWZyYW1lcyhhdWRpb19kYXRhKQogICAgICAgIHdhdmVfZmlsZS5jbG9zZSgpCiAgICAgICAgICAgIAogICAgZGVmIHJldHJpZXZlX3Byb2Nlc3NlZF9kYXRhKHNlbGYpOgogICAgICAgICIiIlJldHJpZXZlIHByb2Nlc3NlZCBkYXRhIGZyb20gb3V0cHV0IHBhdGguIiIiCiAgICAgICAgaWYgbm90IG9zLnBhdGguZXhpc3RzKHNlbGYub3V0cHV0X3BhdGgpOgogICAgICAgICAgICByZXR1cm4gTm9uZQogICAgICAgIHdpdGggb3BlbihzZWxmLm91dHB1dF9wYXRoLCAncmInKSBhcyBmaWxlOgogICAgICAgICAgICByZXR1cm4gZmlsZS5yZWFkKCkKCiAgICBkZWYgZW5jb2RlX3Byb2Nlc3NlZF9kYXRhKHNlbGYsIGRhdGEpOgogICAgICAgICIiIkVuY29kZSBwcm9jZXNzZWQgZGF0YSB0byBiYXNlNjQgc3RyaW5nLiIiIgogICAgICAgIHJldHVybiBiYXNlNjQuYjY0ZW5jb2RlKGRhdGEuZW5jb2RlKCd1dGYtOCcpKS5kZWNvZGUoJ3V0Zi04JykKCiAgICBkZWYgZGVjb2RlX3Byb2Nlc3NlZF9kYXRhKHNlbGYsIGJhc2U2NF9zdHJpbmcpOgogICAgICAgICIiIkRlY29kZSBiYXNlNjQgc3RyaW5nIHRvIHByb2Nlc3NlZCBkYXRhLiIiIgogICAgICAgIHJldHVybiBiYXNlNjQuYjY0ZGVjb2RlKGJhc2U2NF9zdHJpbmcpLmRlY29kZSgndXRmLTgnKQ=='),
    ('whisper.py', 'aW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBzdWJwcm9jZXNzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKZnJvbSBsb2d1cnUgaW1wb3J0IGxvZ2dlcgoKZGVmIHJ1bl93aGlzcGVyKAogICAgd2hpc3Blcl9iaW49Im1vZHVsZXMvd2hpc3Blci93aGlzcGVyLmNwcC9tYWluIiwKICAgIGZpbGVfcGF0aD0ibW9kdWxlcy93aGlzcGVyL2luL2pmay53YXYiLAogICAgbW9kZWxfcGF0aD0ibW9kdWxlcy93aGlzcGVyL3doaXNwZXIuY3BwL21vZGVscy9nZ21sLWJhc2UuZW4uYmluIiwKKToKICAgIGZpbGVfcGF0aCA9IFBhdGgoZmlsZV9wYXRoKQogICAgbW9kZWxfcGF0aCA9IFBhdGgobW9kZWxfcGF0aCkKICAgIHdoaXNwZXJfYmluID0gUGF0aCh3aGlzcGVyX2JpbikKICAgIHRyeToKICAgICAgICByZXN1bHQgPSBzdWJwcm9jZXNzLnJ1bigKICAgICAgICAgICAgW2Yie3doaXNwZXJfYmlufSIsICItbSIsIGYie21vZGVsX3BhdGh9IiwgIi1mIiwgZiJ7ZmlsZV9wYXRofSJdLAogICAgICAgICAgICBzdGRvdXQ9c3VicHJvY2Vzcy5QSVBFLAogICAgICAgICAgICBzdGRlcnI9c3VicHJvY2Vzcy5QSVBFLAogICAgICAgICAgICBjaGVjaz1UcnVlLAogICAgICAgICkKICAgICAgICBsb2dnZXIuZGVidWcocmVzdWx0LnN0ZG91dC5kZWNvZGUoInV0Zi04IikpCiAgICAgICAgcmV0dXJuIHJlc3VsdC5zdGRvdXQuZGVjb2RlKCJ1dGYtOCIpCiAgICBleGNlcHQgc3VicHJvY2Vzcy5DYWxsZWRQcm9jZXNzRXJyb3IgYXMgZXJyb3I6CiAgICAgICAgbG9nZ2VyLmVycm9yKGVycm9yKQogICAgICAgIHJldHVybiBlcnJvcgogICAgZXhjZXB0IFJ1bnRpbWVFcnJvciBhcyBlcnJvcjoKICAgICAgICBsb2dnZXIuZXJyb3IoZXJyb3IpCiAgICAgICAgcmV0dXJuIGVycm9yCgoKZGVmIHBhcnNlX2FyZ3MoKToKICAgIHBhcnNlciA9IGFyZ3BhcnNlLkFyZ3VtZW50UGFyc2VyKCkKICAgIHBhcnNlci5hZGRfYXJndW1lbnQoCiAgICAgICAgIi1mIiwgIi0tZmlsZV9wYXRoIiwgZGVmYXVsdD0ibW9kdWxlcy93aGlzcGVyL2lucHV0L2pmay53YXYiLCB0eXBlPXN0ciwgcmVxdWlyZWQ9RmFsc2UKICAgICkKICAgIHBhcnNlci5hZGRfYXJndW1lbnQoCiAgICAgICAgIi1tIiwKICAgICAgICAiLS1tb2RlbF9wYXRoIiwKICAgICAgICBkZWZhdWx0PSJtb2R1bGVzL3doaXNwZXIvd2hpc3Blci5jcHAvbW9kZWxzL2dnbWwtYmFzZS5lbi5iaW4iLAogICAgICAgIHR5cGU9c3RyLAogICAgICAgIHJlcXVpcmVkPUZhbHNlLAogICAgKQogICAgcGFyc2VyLmFkZF9hcmd1bWVudCgiLXciLCAiLS13aGlzcGVyX2JpbiIsIGRlZmF1bHQ9Im1vZHVsZXMvd2hpc3Blci93aGlzcGVyLmNwcC9tYWluIiwgdHlwZT1zdHIpCiAgICBhcmdzID0gcGFyc2VyLnBhcnNlX2FyZ3MoKQogICAgcmV0dXJuIGFyZ3MKCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgogICAgYXJncyA9IHBhcnNlX2FyZ3MoKQogICAgcnVuX3doaXNwZXIoKip2YXJzKGFyZ3MpKQo='),
    ('convert_file.py', 'aW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBzdWJwcm9jZXNzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAoKCgpkZWYgY29udmVydF90b193YXYoZmlsZV9wYXRoKToKICAgIGlucHV0X25hbWUgPSBQYXRoKGZpbGVfcGF0aCkKICAgIG91dHB1dF9uYW1lID0gaW5wdXRfbmFtZS5uYW1lLmZvcm1hdCgid2F2IikKICAgIG91dHB1dF9wYXRoID0gUGF0aChmIm1vZHVsZXMvd2hpc3Blci9vdXQve291dHB1dF9uYW1lfSIpCiAgICBzdWJwcm9jZXNzLnJ1bigKICAgICAgICBbCiAgICAgICAgICAgICJmZm1wZWciLAogICAgICAgICAgICAiLWkiLAogICAgICAgICAgICBmIntpbnB1dF9uYW1lfSIsCiAgICAgICAgICAgICItYXIiLAogICAgICAgICAgICAiMTYwMDAiLAogICAgICAgICAgICAiLWFjIiwKICAgICAgICAgICAgIjEiLAogICAgICAgICAgICAiLWM6YSIsCiAgICAgICAgICAgICJwY21fczE2bGUiLAogICAgICAgICAgICBmIntvdXRwdXRfcGF0aH0iLAogICAgICAgIF0sCiAgICAgICAgY2hlY2s9VHJ1ZSwKICAgICkKCgpkZWYgcGFyc2VfYXJncygpOgogICAgcGFyc2VyID0gYXJncGFyc2UuQXJndW1lbnRQYXJzZXIoKQogICAgcGFyc2VyLmFkZF9hcmd1bWVudCgiLWYiLCAiLS1maWxlX3BhdGgiLCB0eXBlPXN0ciwgcmVxdWlyZWQ9VHJ1ZSkKICAgIGFyZ3MgPSBwYXJzZXIucGFyc2VfYXJncygpCiAgICByZXR1cm4gYXJncwoKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBmaWxlX3BhdGggPSBwYXJzZV9hcmdzKCkuZmlsZV9wYXRoCiAgICBjb252ZXJ0X3RvX3dhdihmaWxlX3BhdGgpCg=='),
]

for relative_path, encoded_content in file_data:
    full_path = os.path.join(folder_path, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as f:
        f.write(base64.b64decode(encoded_content))
    print(f'Created: {full_path}')
command = ['bash', 'modules/whisper/install_whisper.sh']
subprocess.run(command, check=True)