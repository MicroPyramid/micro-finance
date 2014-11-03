// JavaScript Document
$(document).ready(function (e) {
  //text-box focus
  $(".text-box").focus(function (e) {
    $(this).css("background", "#e8f6f4")
  });
  $(".text-box").blur(function (e) {
    $(this).css("background", "#fff")
  });
  //text-box focus ends above
  //login form replace div
  $("#frgt-btn").click(function (e) {
    $(".login-form").css("display", "none")
    $(".reset-form").css("display", "block")
  });
  //login form replace div
  //date picker
  $(function () {
    $("#datepicker").datepicker({
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });
  $(function () {
    $("#date-picker-gc").datepicker({
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });
  $(function () {
    $("#date-picker-cc").datepicker({
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });
  $(function () {
    $("#datepicker-dob").datepicker({
      changeMonth: true,
      changeYear: true
    });
  });
  //datepicker
  //slide togle
  $(".anc1").click(function () {
    $("#tog-div1").slideToggle('slow', function () {

    });
  });
  $(".anc2").click(function () {
    $("#tog-div2").slideToggle('slow', function () {

    });
  });
  $(".anc3").click(function () {
    $("#tog-div3").slideToggle('slow', function () {

    });
  });
  $(".anc4").click(function () {
    $("#tog-div4").slideToggle('slow', function () {
    });
  });
  //slide togle
  //vertical bar
  $(".toggle-btn").click(function () {
    $(".nav-2").animate({
      width: 'toggle'
    });
  });
  $(".mem").click(function () {
    $(".mem-drop").slideToggle('slow', function () {});
  });
  $(".acc").click(function () {
    $(".acc-drop").slideToggle('slow', function () {});
  });
  $(".sav").click(function () {
    $(".sav-drop").slideToggle('slow', function () {});
  });
  $(".loan").click(function () {
    $(".loan-drop").slideToggle('slow', function () {});
  });
  $(".more").click(function () {
    $(".more-drop").slideToggle('slow', function () {});
  });
  //vertical bar
  //ready function ended below
});