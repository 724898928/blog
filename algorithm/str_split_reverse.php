<?php


$str = '...aaa..bbbb.....ccccc..dd';

$len = strlen($str);
$str_dot = '';
$str_zimu = '';
$pre_is_dot = 1;
$arr = array();
for($i = 0; $i < $len; $i++){
    
    if(($pre_is_dot && '.' != $str[$i]) || (!$pre_is_dot && '.' == $str[$i])){
        

        if(!empty($str_dot)){
            $arr[] = $str_dot;
        }

        if(!empty($str_zimu)){
            $arr[] = $str_zimu;
        }
        $str_dot = '';
        $str_zimu = '';
        

    }

    if($str[$i] == '.'){
        $str_dot .= $str[i];
    }else{
        $str_zimu .= $str[$i];
    }


    if('.' != $str[$i]){
        $pre_is_dot = 0;
    }else{
        $pre_is_dot = 1;
    }
}
if(!empty($str_dot)){
    $arr[] = $str_dot;
}
if(!empty($str_zimu)){
    $arr[] = $str_zimu;
}
$alen = count($arr);
for($j = $alen-1; $j > 0; $j--){
    echo $arr[$j];
}
