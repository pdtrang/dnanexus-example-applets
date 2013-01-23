#!/usr/bin/env python
# parallel_bwa 0.0.1
# Generated by dx-app-wizard.
#
# Parallelized execution pattern: Your app will generate multiple jobs
# to perform some computation in parallel, followed by a final
# "postprocess" stage that will perform any additional computations as
# necessary.
#
# See http://wiki.dnanexus.com/Building-Your-First-DNAnexus-App for
# instructions on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy

@dxpy.entry_point('bwa_controller')
def process(left_reads, right_reads, indexed_reference, aln_params, sampe_params, bwa_aligner):

    output = {"BAMs": []}

    bwa_applet = dxpy.DXApplet(bwa_aligner)

    for x, y in zip(left_reads, right_reads):
        for i in range(len(dxpy.DXJob(x).describe()['output']['fastqgz_chunks'])):
            left_chunk = dxpy.DXJob(x).describe()['output']['fastqgz_chunks'][i]
            right_chunk = dxpy.DXJob(y).describe()['output']['fastqgz_chunks'][i]

            bwa_job = bwa_applet.run({"left_reads": left_chunk, "right_reads":right_chunk, "indexed_reference": indexed_reference, "aln_params": aln_params})
            output["BAMs"].append({"job": bwa_job.get_id(), "field": "BAM"})

    return output

@dxpy.entry_point('main')
def main(fastq_gz_left_reads, fastq_gz_right_reads, indexed_reference, reads_per_chunk=25000000, aln_params="", sampe_params="-r '@RG\tID:1\tPL:ILLUMINA\tPU:None\tLB:1\tSM:1'"):

    picard_merge = applet("picard_merge_sam_files")
    if picard_merge == None:
        raise dxpy.AppError("unable to find applet called 'picard_merge_sam_files'.  Please copy into your project from the collection of developer applets")

    splitter = applet("fastq_splitter")
    if splitter == None:
        raise dxpy.AppError("unable to find applet called 'fastq_splitter'.  Please copy into your project from the collection of developer applets")

    bwa_aligner = applet("bwa_aligner")
    if bwa_aligner == None:
        raise dxpy.AppError("unable to find applet called 'bwa_aligner'.  Please copy into your project from the collection of developer applets")


    bwa_controller_input = {"left_reads": [], "right_reads": [], "indexed_reference": indexed_reference, "aln_params":aln_params, "sampe_params":sampe_params, "bwa_aligner": bwa_aligner.get_id()}
    bwa_subjobs = []
    for x, y in zip(fastq_gz_left_reads, fastq_gz_right_reads):
        left_job = splitter.run({"fastqgz": x, "reads_per_chunk": reads_per_chunk})
        right_job = splitter.run({"fastqgz": x, "reads_per_chunk": reads_per_chunk})
        bwa_controller_input["left_reads"].append(left_job.get_id())
        bwa_controller_input["right_reads"].append(right_job.get_id())
        bwa_subjobs.extend([left_job, right_job])
        
    bwa_controller_job = dxpy.new_dxjob(fn_input=bwa_controller_input, fn_name='bwa_controller', depends_on=bwa_subjobs)

    picard_merge_job = picard_merge.run({"BAMs": {"job": bwa_controller_job.get_id(), "field": "BAMs"}})

    print picard_merge_job.get_id()

    output = {"BAM": {"job": picard_merge_job.get_id(), "field": "BAM"}}

    return output

def applet(name):
    return find_in_project(name=name, classname="applet", return_handler=True, zero_ok=True)

def find_in_project(**kwargs):
    kwargs["project"] = os.environ["DX_PROJECT_CONTEXT_ID"]
    return dxpy.find_one_data_object(**kwargs)

dxpy.run()
