////le cid du plus grand compiled_kernel_size////

SELECT cid FROM compilations 
WHERE compiled_kernel_size = (SELECT MAX(compiled_kernel_size)
FROM compilations);

////Number of kernel compiled par version////

SELECT compiled_kernel_version, count(cid) FROM compilations GROUP BY
compiled_kernel_version;

////Number of failures per version////

select compiled_kernel_version, count(cid) from compilations 
where (compiled_kernel_size < 0) group by compiled_kernel_version;

////Number of failures  total////

SELECT count(cid) FROM compilations 
WHERE compiled_kernel_size < 0;

////Number of cpu_max_frequency per version////

SELECT compiled_kernel_version, count(DISTINCT cpu_max_frequency) 
FROM hardware_environment h1, compilations c1
WHERE (h1.hid = c1.hid)
GROUP BY compiled_kernel_version;

////Les 10 premiers lignes d'une kernel_version donnée////

select * from `compilations`
where compiled_kernel_version= 4.15
order by cid desc 
limit 10;