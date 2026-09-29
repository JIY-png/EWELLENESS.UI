document.addEventListener("DOMContentLoaded", function () {
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const sidebar = document.getElementById("sidebar");
    const clock = document.getElementById("clock");

    /* ============================= */
    /* MOBILE SIDEBAR */
    /* ============================= */

    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener("click", function () {
            sidebar.classList.toggle("show");
        });
    }

    /* ============================= */
    /* LIVE CLOCK */
    /* ============================= */

    function updateClock() {
        const now = new Date();

        const formattedTime = now.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });

        const formattedDate = now.toLocaleDateString([], {
            year: "numeric",
            month: "short",
            day: "numeric"
        });

        if (clock) {
            clock.textContent = `${formattedDate} | ${formattedTime}`;
        }
    }

    updateClock();
    setInterval(updateClock, 1000);

    /* ============================= */
    /* DASHBOARD LIVE DATA */
    /* ============================= */

    async function refreshDashboardData() {
        try {
            const response = await fetch("/api/dashboard-data");

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            const totalPatients = document.querySelector("[data-live='total_patients']");
            const totalRecords = document.querySelector("[data-live='total_records']");
            const attentionRecords = document.querySelector("[data-live='attention_records']");
            const documentationReduction = document.querySelector("[data-live='documentation_reduction']");

            if (totalPatients) {
                totalPatients.textContent = data.stats.total_patients;
            }

            if (totalRecords) {
                totalRecords.textContent = data.stats.total_records;
            }

            if (attentionRecords) {
                attentionRecords.textContent = data.stats.attention_records;
            }

            if (documentationReduction) {
                documentationReduction.textContent = data.stats.documentation_reduction + "%";
            }

            // Update BMI chart data
            const bmiChart = document.getElementById("bmiLineChart");
            if (bmiChart) {
                bmiChart.setAttribute("data-records", JSON.stringify(data.bmi_chart_records));
                // Trigger chart redraw
                const bmiChartNote = document.getElementById("bmiLineChartNote");
                if (bmiChartNote) {
                    bmiChartNote.textContent = "BMI trend updated.";
                }
            }

            // Update donut chart
            const donutChart = document.querySelector(".donut-chart");
            if (donutChart) {
                donutChart.setAttribute("data-normal", data.stats.normal_records);
                donutChart.setAttribute("data-attention", data.stats.attention_records);

                const normal = data.stats.normal_records;
                const attention = data.stats.attention_records;
                const total = normal + attention;

                if (total > 0) {
                    const normalDegrees = (normal / total) * 360;

                    donutChart.style.background = `
                        conic-gradient(
                            #0b9f6a 0deg,
                            #0b9f6a ${normalDegrees}deg,
                            #dc2626 ${normalDegrees}deg,
                            #dc2626 360deg
                        )
                    `;
                }

                // Update donut center text
                const donutCenter = donutChart.querySelector(".donut-center strong");
                if (donutCenter) {
                    donutCenter.textContent = total;
                }
            }

            // Update status trends bars
            const reportBarFills = document.querySelectorAll(".report-bar-fill");
            data.status_trends.forEach(function (item, index) {
                if (reportBarFills[index]) {
                    reportBarFills[index].setAttribute("data-percentage", item.percentage);
                    reportBarFills[index].style.width = item.percentage + "%";
                }
            });

        } catch (error) {
            console.log("Dashboard refresh skipped:", error);
        }
    }

    refreshDashboardData();
    setInterval(refreshDashboardData, 10000);

    /* ============================= */
    /* DASHBOARD BAR CHARTS */
    /* ============================= */

    const dashboardBarFills = document.querySelectorAll(".bar-fill");

    dashboardBarFills.forEach(function (bar) {
        const percentage = bar.getAttribute("data-percentage");

        if (percentage !== null) {
            bar.style.width = percentage + "%";
        }
    });

    /* ============================= */
    /* REPORTS PAGE BAR CHARTS */
    /* This fixes 0-count bars showing as full blue bars */
    /* ============================= */

    const reportBarFills = document.querySelectorAll(".report-bar-fill");

    reportBarFills.forEach(function (bar) {
        const percentage = bar.getAttribute("data-percentage");

        if (percentage !== null) {
            bar.style.width = percentage + "%";
        } else {
            bar.style.width = "0%";
        }
    });

    /* ============================= */
    /* DONUT CHART */
    /* ============================= */

    const donutChart = document.querySelector(".donut-chart");

    if (donutChart) {
        const normal = Number(donutChart.getAttribute("data-normal")) || 0;
        const attention = Number(donutChart.getAttribute("data-attention")) || 0;
        const total = normal + attention;

        if (total > 0) {
            const normalDegrees = (normal / total) * 360;

            donutChart.style.background = `
                conic-gradient(
                    #0b9f6a 0deg,
                    #0b9f6a ${normalDegrees}deg,
                    #dc2626 ${normalDegrees}deg,
                    #dc2626 360deg
                )
            `;
        }
    }

    /* ============================= */
    /* PRINT OR SAVE PDF BUTTON */
    /* ============================= */

    const printReportBtn = document.getElementById("printReportBtn");

    if (printReportBtn) {
        printReportBtn.addEventListener("click", function () {
            window.print();
        });
    }

    /* ============================= */
    /* REUSABLE INSTANT SEARCH */
    /* ============================= */

    function setupInstantSearch(inputId, clearButtonId, rowSelector, emptyStateId) {
        const input = document.getElementById(inputId);
        const clearButton = document.getElementById(clearButtonId);
        const rows = document.querySelectorAll(rowSelector);
        const emptyState = document.getElementById(emptyStateId);

        if (!input || rows.length === 0) {
            return;
        }

        function filterRows() {
            const searchValue = input.value.toLowerCase().trim();
            let visibleCount = 0;

            rows.forEach(function (row) {
                const rowText = row.getAttribute("data-search") || "";
                const searchableText = rowText.toLowerCase();

                if (searchableText.includes(searchValue)) {
                    row.style.display = "";
                    visibleCount += 1;
                } else {
                    row.style.display = "none";
                }
            });

            if (emptyState) {
                emptyState.style.display = visibleCount === 0 ? "block" : "none";
            }
        }

        input.addEventListener("input", filterRows);

        if (clearButton) {
            clearButton.addEventListener("click", function () {
                input.value = "";
                filterRows();
                input.focus();
            });
        }

        filterRows();
    }

    /* ============================= */
    /* PATIENT REGISTRY SEARCH */
    /* ============================= */

    setupInstantSearch(
        "patientRegistrySearch",
        "clearPatientRegistrySearch",
        ".patient-registry-row",
        "patientRegistryNoResults"
    );

    /* ============================= */
    /* EHR RECORDS SEARCH */
    /* ============================= */

    setupInstantSearch(
        "ehrPatientSearch",
        "clearEhrPatientSearch",
        ".ehr-patient-row",
        "ehrPatientNoResults"
    );

    /* ============================= */
    /* PATIENT RECORD HISTORY SEARCH */
    /* ============================= */

    setupInstantSearch(
        "patientRecordSearch",
        "clearPatientRecordSearch",
        ".patient-record-row",
        "patientRecordNoResults"
    );
});

/* ============================= */
/* CLEAN BIRTH DATE INPUT */
/* Manual MM/DD/YYYY + Calendar Icon */
/* ============================= */

document.addEventListener("DOMContentLoaded", function () {
    const birthDateText = document.getElementById("birthDateText");
    const birthDatePicker = document.getElementById("birthDatePicker");
    const openBirthDatePicker = document.getElementById("openBirthDatePicker");

    if (!birthDateText || !birthDatePicker || !openBirthDatePicker) {
        return;
    }

    function formatToMMDDYYYY(value) {
        const cleaned = value.replace(/\D/g, "").slice(0, 8);

        if (cleaned.length >= 5) {
            return cleaned.slice(0, 2) + "/" + cleaned.slice(2, 4) + "/" + cleaned.slice(4);
        }

        if (cleaned.length >= 3) {
            return cleaned.slice(0, 2) + "/" + cleaned.slice(2);
        }

        return cleaned;
    }

    function convertDatePickerToText(value) {
        if (!value) {
            return "";
        }

        const parts = value.split("-");
        const year = parts[0];
        const month = parts[1];
        const day = parts[2];

        return month + "/" + day + "/" + year;
    }

    function convertTextToDatePicker(value) {
        const parts = value.split("/");

        if (parts.length !== 3) {
            return "";
        }

        const month = parts[0];
        const day = parts[1];
        const year = parts[2];

        if (month.length !== 2 || day.length !== 2 || year.length !== 4) {
            return "";
        }

        return year + "-" + month + "-" + day;
    }

    birthDateText.addEventListener("input", function () {
        birthDateText.value = formatToMMDDYYYY(birthDateText.value);

        const pickerValue = convertTextToDatePicker(birthDateText.value);

        if (pickerValue) {
            birthDatePicker.value = pickerValue;
        }
    });

    openBirthDatePicker.addEventListener("click", function () {
        if (birthDatePicker.showPicker) {
            birthDatePicker.showPicker();
        } else {
            birthDatePicker.click();
        }
    });

    birthDatePicker.addEventListener("change", function () {
        birthDateText.value = convertDatePickerToText(birthDatePicker.value);
    });
});

/* ============================= */
/* SECURITY LOG SEARCH + FILTER */
/* ============================= */

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("securityLogSearch");
    const roleFilter = document.getElementById("securityRoleFilter");
    const actionFilter = document.getElementById("securityActionFilter");
    const clearButton = document.getElementById("clearSecurityFilters");
    const rows = document.querySelectorAll(".security-log-row");
    const noResults = document.getElementById("securityLogNoResults");

    if (!searchInput || !roleFilter || !actionFilter || rows.length === 0) {
        return;
    }

    function filterSecurityLogs() {
        const searchValue = searchInput.value.toLowerCase().trim();
        const selectedRole = roleFilter.value;
        const selectedAction = actionFilter.value;
        let visibleCount = 0;

        rows.forEach(function (row) {
            const rowText = (row.getAttribute("data-search") || "").toLowerCase();
            const rowRole = row.getAttribute("data-role") || "";
            const rowAction = (row.getAttribute("data-action") || "").toLowerCase();

            const matchesSearch = rowText.includes(searchValue);
            const matchesRole = selectedRole === "all" || rowRole === selectedRole;
            const matchesAction = selectedAction === "all" || rowAction.includes(selectedAction);

            if (matchesSearch && matchesRole && matchesAction) {
                row.style.display = "";
                visibleCount += 1;
            } else {
                row.style.display = "none";
            }
        });

        if (noResults) {
            noResults.style.display = visibleCount === 0 ? "block" : "none";
        }
    }

    searchInput.addEventListener("input", filterSecurityLogs);
    roleFilter.addEventListener("change", filterSecurityLogs);
    actionFilter.addEventListener("change", filterSecurityLogs);

    if (clearButton) {
        clearButton.addEventListener("click", function () {
            searchInput.value = "";
            roleFilter.value = "all";
            actionFilter.value = "all";
            filterSecurityLogs();
            searchInput.focus();
        });
    }

    filterSecurityLogs();
});

/* ============================= */
/* TOAST NOTIFICATIONS */
/* ============================= */

document.addEventListener("DOMContentLoaded", function () {
    const toasts = document.querySelectorAll(".toast-message");

    toasts.forEach(function (toast) {
        const closeButton = toast.querySelector(".toast-close");

        function removeToast() {
            toast.classList.add("hide");

            setTimeout(function () {
                toast.remove();
            }, 220);
        }

        if (closeButton) {
            closeButton.addEventListener("click", removeToast);
        }

        setTimeout(removeToast, 3500);
    });
});

/* ============================= */
/* USER MANAGEMENT SEARCH + FILTER */
/* ============================= */

document.addEventListener("DOMContentLoaded", function () {
    const userSearch = document.getElementById("userSearch");
    const userRoleFilter = document.getElementById("userRoleFilter");
    const clearUserFilters = document.getElementById("clearUserFilters");
    const userRows = document.querySelectorAll(".user-row");
    const userNoResults = document.getElementById("userNoResults");

    if (!userSearch || !userRoleFilter || userRows.length === 0) {
        return;
    }

    function filterUsers() {
        const searchValue = userSearch.value.toLowerCase().trim();
        const selectedRole = userRoleFilter.value;
        let visibleCount = 0;

        userRows.forEach(function (row) {
            const rowText = (row.getAttribute("data-search") || "").toLowerCase();
            const rowRole = row.getAttribute("data-role") || "";

            const matchesSearch = rowText.includes(searchValue);
            const matchesRole = selectedRole === "all" || rowRole === selectedRole;

            if (matchesSearch && matchesRole) {
                row.style.display = "";
                visibleCount += 1;
            } else {
                row.style.display = "none";
            }
        });

        if (userNoResults) {
            userNoResults.style.display = visibleCount === 0 ? "block" : "none";
        }
    }

    userSearch.addEventListener("input", filterUsers);
    userRoleFilter.addEventListener("change", filterUsers);

    if (clearUserFilters) {
        clearUserFilters.addEventListener("click", function () {
            userSearch.value = "";
            userRoleFilter.value = "all";
            filterUsers();
            userSearch.focus();
        });
    }

    filterUsers();
});

/* ============================= */
/* KIOSK CLOCK */
/* ============================= */

document.addEventListener("DOMContentLoaded", function () {
    const kioskClock = document.getElementById("kioskClock");

    if (!kioskClock) {
        return;
    }

    function updateKioskClock() {
        const now = new Date();

        kioskClock.textContent = now.toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    updateKioskClock();
    setInterval(updateKioskClock, 1000);
});

/* ===================================== */
/* KIOSK TEMPERATURE SIMULATION */
/* ===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const openBtn = document.getElementById("openTempInstructionsBtn");
    const modal = document.getElementById("tempInstructionModal");
    const prevBtn = document.getElementById("tempPrevBtn");
    const nextBtn = document.getElementById("tempNextBtn");

    const stepTitle = document.getElementById("tempStepTitle");
    const stepText = document.getElementById("tempStepText");
    const stepIcon = document.getElementById("tempStepIcon");

    const tempMessage = document.getElementById("tempMessage");
    const tempValue = document.getElementById("tempValue");
    const tempStatus = document.getElementById("tempStatus");
    const tempInput = document.getElementById("temperatureValueInput");

    const startActions = document.getElementById("tempStartActions");
    const measuringActions = document.getElementById("tempMeasuringActions");
    const resultActions = document.getElementById("tempResultActions");

    const cancelBtn = document.getElementById("cancelTempBtn");
    const retryBtn = document.getElementById("retryTempBtn");
    const retrySavedBtn = document.getElementById("retrySavedTempBtn");

    if (!openBtn && !retrySavedBtn) {
        return;
    }

    const steps = [
        {
            icon: '<i class="fa-solid fa-temperature-three-quarters"></i>',
            title: "Step 1: Prepare",
            text: "Make sure your forehead is clean, dry, and free from sweat or cosmetics."
        },
        {
            icon: '<i class="fa-solid fa-ruler"></i>',
            title: "Step 2: Positioning",
            text: "Hold the temperature sensor 1 to 2 cm away from the center of your forehead."
        },
        {
            icon: '<i class="fa-solid fa-check"></i>',
            title: "Step 3: Measurement",
            text: "Keep still while the sensor reads your temperature. The process will only take a few seconds."
        }
    ];

    let currentStep = 0;
    let measuringTimer = null;

    function updateModalStep() {
        stepIcon.innerHTML = steps[currentStep].icon;
        stepTitle.textContent = steps[currentStep].title;
        stepText.textContent = steps[currentStep].text;

        document.querySelectorAll(".temp-step-dots span").forEach(function (dot, index) {
            dot.classList.toggle("active", index === currentStep);
        });

        prevBtn.disabled = currentStep === 0;

        if (currentStep === steps.length - 1) {
            nextBtn.textContent = "Start Measurement";
        } else {
            nextBtn.textContent = "Next";
        }
    }

    function openInstructionModal() {
        currentStep = 0;
        updateModalStep();
        modal.classList.remove("hidden");
    }

    function resetMeasurementScreen() {
        if (tempMessage) {
            tempMessage.textContent = "Ready to measure. Click Start to begin.";
        }

        if (tempValue) {
            tempValue.textContent = "--.- °C";
            tempValue.classList.remove("measuring", "complete");
        }

        if (tempStatus) {
            tempStatus.textContent = "";
            tempStatus.className = "temp-status";
        }

        if (tempInput) {
            tempInput.value = "";
        }

        if (startActions) {
            startActions.classList.remove("hidden");
        }

        if (measuringActions) {
            measuringActions.classList.add("hidden");
        }

        if (resultActions) {
            resultActions.classList.add("hidden");
        }
    }

    function startMeasurement() {
        if (!tempMessage || !tempValue || !tempStatus || !tempInput) {
            return;
        }

        if (startActions) {
            startActions.classList.add("hidden");
        }

        if (resultActions) {
            resultActions.classList.add("hidden");
        }

        if (measuringActions) {
            measuringActions.classList.remove("hidden");
        }

        tempMessage.textContent = "Measuring... Please hold still.";
        tempValue.textContent = "--.- °C";
        tempValue.classList.add("measuring");
        tempValue.classList.remove("complete");

        tempStatus.textContent = "";
        tempStatus.className = "temp-status";
        tempInput.value = "";

        measuringTimer = setTimeout(function () {
            const result = generateTemperatureResult();
            const status = getTemperatureStatus(result);

            tempMessage.textContent = "Measurement complete.";
            tempValue.textContent = result.toFixed(1) + " °C";
            tempValue.classList.remove("measuring");
            tempValue.classList.add("complete");

            tempStatus.textContent = status.label;
            tempStatus.className = "temp-status " + status.className;

            tempInput.value = result.toFixed(1);

            if (measuringActions) {
                measuringActions.classList.add("hidden");
            }

            if (resultActions) {
                resultActions.classList.remove("hidden");
            }
        }, 3000);
    }

    function generateTemperatureResult() {
        const results = [36.2, 36.3, 36.4, 36.5, 36.6, 36.7];
        const randomIndex = Math.floor(Math.random() * results.length);
        return results[randomIndex];
    }

    function getTemperatureStatus(value) {
        if (value < 36.0) {
            return {
                label: "LOW TEMPERATURE",
                className: "warning"
            };
        }

        if (value <= 37.5) {
            return {
                label: "NORMAL TEMPERATURE",
                className: "normal"
            };
        }

        return {
            label: "HIGH TEMPERATURE",
            className: "danger"
        };
    }

    if (openBtn) {
        openBtn.addEventListener("click", openInstructionModal);
    }

    if (retrySavedBtn) {
        retrySavedBtn.addEventListener("click", function () {
            window.location.href = window.location.href;
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", function () {
            if (currentStep > 0) {
                currentStep--;
                updateModalStep();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", function () {
            if (currentStep < steps.length - 1) {
                currentStep++;
                updateModalStep();
            } else {
                modal.classList.add("hidden");
                startMeasurement();
            }
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", function () {
            clearTimeout(measuringTimer);
            resetMeasurementScreen();
        });
    }

    if (retryBtn) {
        retryBtn.addEventListener("click", function () {
            startMeasurement();
        });
    }
});

/* ===================================== */
/* KIOSK BLOOD PRESSURE SIMULATION */
/* ===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const openBtn = document.getElementById("openBpInstructionsBtn");
    const modal = document.getElementById("bpInstructionModal");
    const prevBtn = document.getElementById("bpPrevBtn");
    const nextBtn = document.getElementById("bpNextBtn");

    const stepTitle = document.getElementById("bpStepTitle");
    const stepText = document.getElementById("bpStepText");
    const stepIcon = document.getElementById("bpStepIcon");

    const bpMessage = document.getElementById("bpMessage");
    const bpValue = document.getElementById("bpValue");
    const bpPulse = document.getElementById("bpPulse");
    const bpStatus = document.getElementById("bpStatus");

    const systolicInput = document.getElementById("systolicValueInput");
    const diastolicInput = document.getElementById("diastolicValueInput");
    const pulseInput = document.getElementById("pulseValueInput");

    const startActions = document.getElementById("bpStartActions");
    const measuringActions = document.getElementById("bpMeasuringActions");
    const resultActions = document.getElementById("bpResultActions");

    const cancelBtn = document.getElementById("cancelBpBtn");
    const retryBtn = document.getElementById("retryBpBtn");

    if (!openBtn) {
        return;
    }

    const steps = [
        {
            icon: '<i class="fa-solid fa-chair"></i>',
            title: "Step 1: Sit Properly",
            text: "Sit comfortably with your back supported and your feet flat on the floor."
        },
        {
            icon: '<i class="fa-solid fa-hand"></i>',
            title: "Step 2: Position Your Arm",
            text: "Place your arm on the kiosk arm rest. Keep it relaxed and level with your heart."
        },
        {
            icon: '<i class="fa-solid fa-heart-pulse"></i>',
            title: "Step 3: Stay Still",
            text: "Do not move or talk while the blood pressure monitor is taking your reading."
        }
    ];

    let currentStep = 0;
    let measuringTimer = null;

    function updateModalStep() {
        stepIcon.innerHTML = steps[currentStep].icon;
        stepTitle.textContent = steps[currentStep].title;
        stepText.textContent = steps[currentStep].text;

        document.querySelectorAll(".bp-step-dots span").forEach(function (dot, index) {
            dot.classList.toggle("active", index === currentStep);
        });

        prevBtn.disabled = currentStep === 0;

        if (currentStep === steps.length - 1) {
            nextBtn.textContent = "Start Measurement";
        } else {
            nextBtn.textContent = "Next";
        }
    }

    function openInstructionModal() {
        currentStep = 0;
        updateModalStep();
        modal.classList.remove("hidden");
    }

    function resetMeasurementScreen() {
        bpMessage.textContent = "Ready to measure. Click Start to begin.";
        bpValue.innerHTML = '--/--<small>mmHg</small>';
        bpValue.classList.remove("measuring", "complete");
        bpPulse.textContent = "Pulse: -- bpm";
        bpStatus.textContent = "";
        bpStatus.className = "bp-status";

        systolicInput.value = "";
        diastolicInput.value = "";
        pulseInput.value = "";

        startActions.classList.remove("hidden");
        measuringActions.classList.add("hidden");
        resultActions.classList.add("hidden");
    }

    function startMeasurement() {
        startActions.classList.add("hidden");
        resultActions.classList.add("hidden");
        measuringActions.classList.remove("hidden");

        bpMessage.textContent = "Measuring... Please stay still.";
        bpValue.innerHTML = '--/--<small>mmHg</small>';
        bpValue.classList.add("measuring");
        bpValue.classList.remove("complete");
        bpPulse.textContent = "Pulse: -- bpm";
        bpStatus.textContent = "";
        bpStatus.className = "bp-status";

        systolicInput.value = "";
        diastolicInput.value = "";
        pulseInput.value = "";

        measuringTimer = setTimeout(function () {
            const result = generateBloodPressureResult();
            const status = getBloodPressureStatus(result.systolic, result.diastolic);

            bpMessage.textContent = "Measurement complete.";
            bpValue.innerHTML = result.systolic + "/" + result.diastolic + "<small>mmHg</small>";
            bpValue.classList.remove("measuring");
            bpValue.classList.add("complete");

            bpPulse.textContent = "Pulse: " + result.pulse + " bpm";

            bpStatus.textContent = status.label;
            bpStatus.className = "bp-status " + status.className;

            systolicInput.value = result.systolic;
            diastolicInput.value = result.diastolic;
            pulseInput.value = result.pulse;

            measuringActions.classList.add("hidden");
            resultActions.classList.remove("hidden");
        }, 3500);
    }

    function generateBloodPressureResult() {
        const normalResults = [
            { systolic: 118, diastolic: 76, pulse: 76 },
            { systolic: 120, diastolic: 80, pulse: 78 },
            { systolic: 122, diastolic: 79, pulse: 74 },
            { systolic: 116, diastolic: 75, pulse: 72 },
            { systolic: 124, diastolic: 82, pulse: 80 }
        ];

        const randomIndex = Math.floor(Math.random() * normalResults.length);
        return normalResults[randomIndex];
    }

    function getBloodPressureStatus(systolic, diastolic) {
        if (systolic < 90 || diastolic < 60) {
            return {
                label: "LOW BLOOD PRESSURE",
                className: "warning"
            };
        }

        if (systolic >= 140 || diastolic >= 90) {
            return {
                label: "HIGH BLOOD PRESSURE",
                className: "danger"
            };
        }

        return {
            label: "NORMAL BLOOD PRESSURE",
            className: "normal"
        };
    }

    openBtn.addEventListener("click", openInstructionModal);

    prevBtn.addEventListener("click", function () {
        if (currentStep > 0) {
            currentStep--;
            updateModalStep();
        }
    });

    nextBtn.addEventListener("click", function () {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateModalStep();
        } else {
            modal.classList.add("hidden");
            startMeasurement();
        }
    });

    cancelBtn.addEventListener("click", function () {
        clearTimeout(measuringTimer);
        resetMeasurementScreen();
    });

    retryBtn.addEventListener("click", function () {
        startMeasurement();
    });
});

/* ===================================== */
/* KIOSK HEIGHT SIMULATION */
/* ===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const openBtn = document.getElementById("openHeightInstructionsBtn");
    const modal = document.getElementById("heightInstructionModal");
    const prevBtn = document.getElementById("heightPrevBtn");
    const nextBtn = document.getElementById("heightNextBtn");

    const stepTitle = document.getElementById("heightStepTitle");
    const stepText = document.getElementById("heightStepText");
    const stepIcon = document.getElementById("heightStepIcon");

    const heightMessage = document.getElementById("heightMessage");
    const heightValue = document.getElementById("heightValue");
    const heightStatus = document.getElementById("heightStatus");
    const heightInput = document.getElementById("heightValueInput");

    const startActions = document.getElementById("heightStartActions");
    const measuringActions = document.getElementById("heightMeasuringActions");
    const resultActions = document.getElementById("heightResultActions");

    const cancelBtn = document.getElementById("cancelHeightBtn");
    const retryBtn = document.getElementById("retryHeightBtn");

    if (!openBtn) {
        return;
    }

    const steps = [
        {
            icon: '<i class="fa-solid fa-ruler-vertical"></i>',
            title: "Step 1: Stand Straight",
            text: "Stand on the marked area with your back upright and your feet flat on the floor."
        },
        {
            icon: '<i class="fa-solid fa-person"></i>',
            title: "Step 2: Face Forward",
            text: "Keep your head straight, face forward, and avoid bending your knees."
        },
        {
            icon: '<i class="fa-solid fa-check"></i>',
            title: "Step 3: Stay Still",
            text: "Remain still while the height sensor reads your measurement."
        }
    ];

    let currentStep = 0;
    let measuringTimer = null;

    function updateModalStep() {
        stepIcon.innerHTML = steps[currentStep].icon;
        stepTitle.textContent = steps[currentStep].title;
        stepText.textContent = steps[currentStep].text;

        document.querySelectorAll(".height-step-dots span").forEach(function (dot, index) {
            dot.classList.toggle("active", index === currentStep);
        });

        prevBtn.disabled = currentStep === 0;

        if (currentStep === steps.length - 1) {
            nextBtn.textContent = "Start Measurement";
        } else {
            nextBtn.textContent = "Next";
        }
    }

    function openInstructionModal() {
        currentStep = 0;
        updateModalStep();
        modal.classList.remove("hidden");
    }

    function resetMeasurementScreen() {
        heightMessage.textContent = "Ready to measure. Click Start to begin.";
        heightValue.innerHTML = '--.-<small>cm</small>';
        heightValue.classList.remove("measuring", "complete");
        heightStatus.textContent = "";
        heightStatus.className = "height-status";
        heightInput.value = "";

        startActions.classList.remove("hidden");
        measuringActions.classList.add("hidden");
        resultActions.classList.add("hidden");
    }

    function startMeasurement() {
        startActions.classList.add("hidden");
        resultActions.classList.add("hidden");
        measuringActions.classList.remove("hidden");

        heightMessage.textContent = "Measuring... Please stand still.";
        heightValue.innerHTML = '--.-<small>cm</small>';
        heightValue.classList.add("measuring");
        heightValue.classList.remove("complete");
        heightStatus.textContent = "";
        heightStatus.className = "height-status";
        heightInput.value = "";

        measuringTimer = setTimeout(function () {
            const result = generateHeightResult();
            const status = getHeightStatus(result);

            heightMessage.textContent = "Measurement complete.";
            heightValue.innerHTML = result.toFixed(1) + "<small>cm</small>";
            heightValue.classList.remove("measuring");
            heightValue.classList.add("complete");

            heightStatus.textContent = status.label;
            heightStatus.className = "height-status " + status.className;
            heightInput.value = result.toFixed(1);

            measuringActions.classList.add("hidden");
            resultActions.classList.remove("hidden");
        }, 3000);
    }

    function generateHeightResult() {
        const results = [152.4, 155.6, 158.2, 160.5, 162.7, 165.3, 168.1, 170.4];
        const randomIndex = Math.floor(Math.random() * results.length);
        return results[randomIndex];
    }

    function getHeightStatus(value) {
        if (value < 120) {
            return {
                label: "BELOW AVERAGE HEIGHT",
                className: "warning"
            };
        }

        if (value <= 190) {
            return {
                label: "HEIGHT RECORDED",
                className: "normal"
            };
        }

        return {
            label: "ABOVE AVERAGE HEIGHT",
            className: "danger"
        };
    }

    openBtn.addEventListener("click", openInstructionModal);

    prevBtn.addEventListener("click", function () {
        if (currentStep > 0) {
            currentStep--;
            updateModalStep();
        }
    });

    nextBtn.addEventListener("click", function () {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateModalStep();
        } else {
            modal.classList.add("hidden");
            startMeasurement();
        }
    });

    cancelBtn.addEventListener("click", function () {
        clearTimeout(measuringTimer);
        resetMeasurementScreen();
    });

    retryBtn.addEventListener("click", function () {
        startMeasurement();
    });
});

/* ===================================== */
/* KIOSK WEIGHT SIMULATION WITH SCALE ZEROING + STEP-ON COUNTDOWN */
/* ===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const openBtn = document.getElementById("openWeightInstructionsBtn");
    const modal = document.getElementById("weightInstructionModal");
    const prevBtn = document.getElementById("weightPrevBtn");
    const nextBtn = document.getElementById("weightNextBtn");

    const stepTitle = document.getElementById("weightStepTitle");
    const stepText = document.getElementById("weightStepText");
    const stepIcon = document.getElementById("weightStepIcon");

    const weightMessage = document.getElementById("weightMessage");
    const weightValue = document.getElementById("weightValue");
    const weightStatus = document.getElementById("weightStatus");
    const weightInput = document.getElementById("weightValueInput");

    const startActions = document.getElementById("weightStartActions");
    const measuringActions = document.getElementById("weightMeasuringActions");
    const resultActions = document.getElementById("weightResultActions");

    const cancelBtn = document.getElementById("cancelWeightBtn");
    const retryBtn = document.getElementById("retryWeightBtn");

    if (!openBtn) {
        return;
    }

    const steps = [
        {
            icon: '<i class="fa-solid fa-shoe-prints"></i>',
            title: "Step 1: Step Off First",
            text: "Please step away from the weighing platform before starting. This allows the scale to refresh and reset to zero."
        },
        {
            icon: '<i class="fa-solid fa-weight-scale"></i>',
            title: "Step 2: Step on the Scale",
            text: "When the screen tells you to step on, stand on the weighing scale with both feet properly positioned."
        },
        {
            icon: '<i class="fa-solid fa-person-standing"></i>',
            title: "Step 3: Stand Still",
            text: "Keep your body still and avoid holding onto anything while your weight is being measured."
        }
    ];

    let currentStep = 0;
    let calibrationTimer = null;
    let stepOnTimer = null;
    let measuringTimer = null;
    let calibrationInterval = null;
    let stepOnInterval = null;

    function updateModalStep() {
        stepIcon.innerHTML = steps[currentStep].icon;
        stepTitle.textContent = steps[currentStep].title;
        stepText.textContent = steps[currentStep].text;

        document.querySelectorAll(".weight-step-dots span").forEach(function (dot, index) {
            dot.classList.toggle("active", index === currentStep);
        });

        prevBtn.disabled = currentStep === 0;

        if (currentStep === steps.length - 1) {
            nextBtn.textContent = "Start Measurement";
        } else {
            nextBtn.textContent = "Next";
        }
    }

    function openInstructionModal() {
        currentStep = 0;
        updateModalStep();
        modal.classList.remove("hidden");
    }

    function clearAllWeightTimers() {
        clearTimeout(calibrationTimer);
        clearTimeout(stepOnTimer);
        clearTimeout(measuringTimer);
        clearInterval(calibrationInterval);
        clearInterval(stepOnInterval);
    }

    function resetMeasurementScreen() {
        clearAllWeightTimers();

        weightMessage.textContent = "Ready to measure. Click Start to begin.";
        weightValue.innerHTML = '--.-<small>kg</small>';
        weightValue.classList.remove("measuring", "complete");
        weightStatus.textContent = "";
        weightStatus.className = "weight-status";
        weightInput.value = "";

        startActions.classList.remove("hidden");
        measuringActions.classList.add("hidden");
        resultActions.classList.add("hidden");
    }

    function startMeasurement() {
        clearAllWeightTimers();

        startActions.classList.add("hidden");
        resultActions.classList.add("hidden");
        measuringActions.classList.remove("hidden");

        let calibrationCountdown = 5;

        weightMessage.textContent = "Please step off the platform. Calibrating scale...";
        weightValue.innerHTML = calibrationCountdown + '<small>sec</small>';
        weightValue.classList.add("measuring");
        weightValue.classList.remove("complete");
        weightStatus.textContent = "ZEROING SCALE";
        weightStatus.className = "weight-status warning";
        weightInput.value = "";

        calibrationInterval = setInterval(function () {
            calibrationCountdown -= 1;

            if (calibrationCountdown > 0) {
                weightValue.innerHTML = calibrationCountdown + '<small>sec</small>';
            }
        }, 1000);

        calibrationTimer = setTimeout(function () {
            clearInterval(calibrationInterval);
            showStepOnCountdown();
        }, 5000);
    }

    function showStepOnCountdown() {
        let stepOnCountdown = 5;

        weightMessage.textContent = "Step on the platform now.";
        weightValue.innerHTML = stepOnCountdown + '<small>sec</small>';
        weightStatus.textContent = "PLEASE STEP ON";
        weightStatus.className = "weight-status warning";

        stepOnInterval = setInterval(function () {
            stepOnCountdown -= 1;

            if (stepOnCountdown > 0) {
                weightValue.innerHTML = stepOnCountdown + '<small>sec</small>';
            }
        }, 1000);

        stepOnTimer = setTimeout(function () {
            clearInterval(stepOnInterval);
            measureWeight();
        }, 5000);
    }

    function measureWeight() {
        weightMessage.textContent = "Measuring... Please stand still.";
        weightValue.innerHTML = '--.-<small>kg</small>';
        weightStatus.textContent = "MEASURING WEIGHT";
        weightStatus.className = "weight-status warning";

        measuringTimer = setTimeout(function () {
            const result = generateWeightResult();
            const status = getWeightStatus(result);

            weightMessage.textContent = "Measurement complete.";
            weightValue.innerHTML = result.toFixed(1) + "<small>kg</small>";
            weightValue.classList.remove("measuring");
            weightValue.classList.add("complete");

            weightStatus.textContent = status.label;
            weightStatus.className = "weight-status " + status.className;
            weightInput.value = result.toFixed(1);

            measuringActions.classList.add("hidden");
            resultActions.classList.remove("hidden");
        }, 3000);
    }

    function generateWeightResult() {
        const results = [47.8, 50.2, 52.5, 55.0, 58.4, 60.7, 63.1, 66.5, 70.2];
        const randomIndex = Math.floor(Math.random() * results.length);
        return results[randomIndex];
    }

    function getWeightStatus(value) {
        if (value <= 0) {
            return {
                label: "INVALID WEIGHT",
                className: "danger"
            };
        }

        return {
            label: "WEIGHT RECORDED",
            className: "normal"
        };
    }

    openBtn.addEventListener("click", openInstructionModal);

    prevBtn.addEventListener("click", function () {
        if (currentStep > 0) {
            currentStep--;
            updateModalStep();
        }
    });

    nextBtn.addEventListener("click", function () {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateModalStep();
        } else {
            modal.classList.add("hidden");
            startMeasurement();
        }
    });

    cancelBtn.addEventListener("click", function () {
        resetMeasurementScreen();
    });

    retryBtn.addEventListener("click", function () {
        startMeasurement();
    });
});

/* ===================================== */
/* KIOSK BMI CALCULATION */
/* ===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const calculateBtn = document.getElementById("calculateBmiBtn");
    const retryBtn = document.getElementById("retryBmiBtn");
    const recalculateBtn = document.getElementById("recalculateBmiBtn");

    const bmiMessage = document.getElementById("bmiMessage");
    const bmiValue = document.getElementById("bmiValue");
    const bmiStatus = document.getElementById("bmiStatus");

    const startActions = document.getElementById("bmiStartActions");
    const resultActions = document.getElementById("bmiResultActions");

    if (!calculateBtn && !recalculateBtn) {
        return;
    }

    function getStatusClass(category) {
        if (category === "Normal") {
            return "normal";
        }

        if (category === "Invalid") {
            return "danger";
        }

        return "warning";
    }

    function calculateBmiDisplay() {
        const calculatedBmi = bmiValue.getAttribute("data-bmi");
        const bmiCategory = bmiValue.getAttribute("data-category");
        const bmiStatusText = bmiValue.getAttribute("data-status");

        bmiMessage.textContent = "Calculating BMI from height and weight...";
        bmiValue.innerHTML = '--.-<small>kg/m²</small>';
        bmiValue.classList.add("calculating");
        bmiValue.classList.remove("complete");

        bmiStatus.textContent = "";
        bmiStatus.className = "bmi-status";

        startActions.classList.add("hidden");
        resultActions.classList.add("hidden");

        setTimeout(function () {
            bmiMessage.textContent = "BMI calculation complete.";
            bmiValue.innerHTML = calculatedBmi + "<small>kg/m²</small>";
            bmiValue.classList.remove("calculating");
            bmiValue.classList.add("complete");

            bmiStatus.textContent = bmiStatusText;
            bmiStatus.className = "bmi-status " + getStatusClass(bmiCategory);

            resultActions.classList.remove("hidden");
        }, 1200);
    }

    if (calculateBtn) {
        calculateBtn.addEventListener("click", calculateBmiDisplay);
    }

    if (retryBtn) {
        retryBtn.addEventListener("click", calculateBmiDisplay);
    }

    if (recalculateBtn) {
        recalculateBtn.addEventListener("click", function () {
            window.location.href = "{{ url_for('kiosk_bmi_page') }}";
        });
    }
});

/* ===================================== */
/* KIOSK OXYGEN SATURATION SIMULATION */
/* ===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const openBtn = document.getElementById("openSpo2InstructionsBtn");
    const modal = document.getElementById("spo2InstructionModal");
    const prevBtn = document.getElementById("spo2PrevBtn");
    const nextBtn = document.getElementById("spo2NextBtn");

    const stepTitle = document.getElementById("spo2StepTitle");
    const stepText = document.getElementById("spo2StepText");
    const stepIcon = document.getElementById("spo2StepIcon");

    const spo2Message = document.getElementById("spo2Message");
    const spo2Value = document.getElementById("spo2Value");
    const spo2Status = document.getElementById("spo2Status");
    const spo2Input = document.getElementById("spo2ValueInput");

    const startActions = document.getElementById("spo2StartActions");
    const measuringActions = document.getElementById("spo2MeasuringActions");
    const resultActions = document.getElementById("spo2ResultActions");

    const cancelBtn = document.getElementById("cancelSpo2Btn");
    const retryBtn = document.getElementById("retrySpo2Btn");

    if (!openBtn) {
        return;
    }

    const steps = [
        {
            icon: '<i class="fa-solid fa-hand"></i>',
            title: "Step 1: Prepare Your Finger",
            text: "Make sure your finger is clean, dry, and free from nail polish or anything blocking the sensor."
        },
        {
            icon: '<i class="fa-solid fa-fingerprint"></i>',
            title: "Step 2: Place Your Finger",
            text: "Insert your finger properly into the pulse oximeter sensor. Keep it relaxed and centered."
        },
        {
            icon: '<i class="fa-solid fa-lungs"></i>',
            title: "Step 3: Stay Still",
            text: "Keep your finger still while the oxygen saturation reading is being measured."
        }
    ];

    let currentStep = 0;
    let measuringTimer = null;

    function updateModalStep() {
        stepIcon.innerHTML = steps[currentStep].icon;
        stepTitle.textContent = steps[currentStep].title;
        stepText.textContent = steps[currentStep].text;

        document.querySelectorAll(".spo2-step-dots span").forEach(function (dot, index) {
            dot.classList.toggle("active", index === currentStep);
        });

        prevBtn.disabled = currentStep === 0;

        if (currentStep === steps.length - 1) {
            nextBtn.textContent = "Start Measurement";
        } else {
            nextBtn.textContent = "Next";
        }
    }

    function openInstructionModal() {
        currentStep = 0;
        updateModalStep();
        modal.classList.remove("hidden");
    }

    function resetMeasurementScreen() {
        clearTimeout(measuringTimer);

        spo2Message.textContent = "Ready to measure. Click Start to begin.";
        spo2Value.innerHTML = '--<small>%</small>';
        spo2Value.classList.remove("measuring", "complete");
        spo2Status.textContent = "";
        spo2Status.className = "spo2-status";
        spo2Input.value = "";

        startActions.classList.remove("hidden");
        measuringActions.classList.add("hidden");
        resultActions.classList.add("hidden");
    }

    function startMeasurement() {
        startActions.classList.add("hidden");
        resultActions.classList.add("hidden");
        measuringActions.classList.remove("hidden");

        spo2Message.textContent = "Measuring... Please keep your finger still.";
        spo2Value.innerHTML = '--<small>%</small>';
        spo2Value.classList.add("measuring");
        spo2Value.classList.remove("complete");
        spo2Status.textContent = "READING OXYGEN LEVEL";
        spo2Status.className = "spo2-status warning";
        spo2Input.value = "";

        measuringTimer = setTimeout(function () {
            const result = generateSpo2Result();
            const status = getSpo2Status(result);

            spo2Message.textContent = "Measurement complete.";
            spo2Value.innerHTML = result + "<small>%</small>";
            spo2Value.classList.remove("measuring");
            spo2Value.classList.add("complete");

            spo2Status.textContent = status.label;
            spo2Status.className = "spo2-status " + status.className;
            spo2Input.value = result;

            measuringActions.classList.add("hidden");
            resultActions.classList.remove("hidden");
        }, 3000);
    }

    function generateSpo2Result() {
        const results = [96, 97, 98, 99];
        const randomIndex = Math.floor(Math.random() * results.length);
        return results[randomIndex];
    }

    function getSpo2Status(value) {
        if (value < 95) {
            return {
                label: "LOW OXYGEN SATURATION",
                className: "danger"
            };
        }

        if (value <= 100) {
            return {
                label: "NORMAL OXYGEN SATURATION",
                className: "normal"
            };
        }

        return {
            label: "INVALID OXYGEN SATURATION",
            className: "danger"
        };
    }

    openBtn.addEventListener("click", openInstructionModal);

    prevBtn.addEventListener("click", function () {
        if (currentStep > 0) {
            currentStep--;
            updateModalStep();
        }
    });

    nextBtn.addEventListener("click", function () {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateModalStep();
        } else {
            modal.classList.add("hidden");
            startMeasurement();
        }
    });

    cancelBtn.addEventListener("click", function () {
        resetMeasurementScreen();
    });

    retryBtn.addEventListener("click", function () {
        startMeasurement();
    });
});

/* ===================================== */
/* KIOSK PRINT RESULT BUTTON */
/* ===================================== */

document.addEventListener("DOMContentLoaded", function () {
    const printResultBtn = document.getElementById("printResultBtn");

    if (!printResultBtn) {
        return;
    }

    printResultBtn.addEventListener("click", function () {
        window.print();
    });
});

/* ============================= */
/* BMI TREND OVERVIEW LINE GRAPH */
/* Daily / Weekly / Monthly / Yearly / Custom Range */
/* ============================= */

document.addEventListener("DOMContentLoaded", function () {
    const chartContainer = document.getElementById("bmiLineChart");
    const chartSvg = document.getElementById("bmiLineChartSvg");
    const chartRange = document.getElementById("bmiChartRange");
    const chartNote = document.getElementById("bmiLineChartNote");
    const customRangeBox = document.getElementById("bmiCustomRange");
    const startDateInput = document.getElementById("bmiStartDate");
    const endDateInput = document.getElementById("bmiEndDate");

    if (!chartContainer || !chartSvg || !chartRange) {
        return;
    }

    let records = [];

    try {
        records = JSON.parse(chartContainer.getAttribute("data-records") || "[]");
    } catch (error) {
        records = [];
    }

    function parseRecordDate(value) {
        if (!value) {
            return null;
        }

        const parts = value.match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})\s+(AM|PM)$/i);

        if (!parts) {
            const fallbackDate = new Date(value);
            return Number.isNaN(fallbackDate.getTime()) ? null : fallbackDate;
        }

        let hour = Number(parts[4]);
        const minute = Number(parts[5]);
        const meridiem = parts[6].toUpperCase();

        if (meridiem === "PM" && hour !== 12) {
            hour += 12;
        }

        if (meridiem === "AM" && hour === 12) {
            hour = 0;
        }

        return new Date(
            Number(parts[1]),
            Number(parts[2]) - 1,
            Number(parts[3]),
            hour,
            minute
        );
    }

    function prepareRecords() {
        return records
            .map(function (record) {
                return {
                    bmi: Number(record.bmi),
                    category: record.category,
                    patientName: record.patient_name || "Patient",
                    date: parseRecordDate(record.created_at)
                };
            })
            .filter(function (record) {
                return record.date !== null && Number.isFinite(record.bmi) && record.bmi > 0;
            })
            .sort(function (a, b) {
                return a.date - b.date;
            });
    }

    function getStartOfWeek(date) {
        const start = new Date(date);
        const day = start.getDay();

        start.setDate(start.getDate() - day);
        start.setHours(0, 0, 0, 0);

        return start;
    }

    function getEndOfDay(date) {
        const end = new Date(date);
        end.setHours(23, 59, 59, 999);
        return end;
    }

    function getDateFromInput(value, endOfDay) {
        if (!value) {
            return null;
        }

        const parts = value.split("-");

        if (parts.length !== 3) {
            return null;
        }

        const date = new Date(
            Number(parts[0]),
            Number(parts[1]) - 1,
            Number(parts[2])
        );

        if (endOfDay) {
            return getEndOfDay(date);
        }

        date.setHours(0, 0, 0, 0);
        return date;
    }

    function formatShortDate(date) {
        return date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric"
        });
    }

    function formatDateTime(date) {
        return date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric"
        }) + " " + date.toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit"
        });
    }

    function getFilteredRecords(range) {
        const now = new Date();
        const parsedRecords = prepareRecords();

        if (range === "daily") {
            const start = new Date(now);
            start.setHours(0, 0, 0, 0);

            const end = getEndOfDay(now);

            return parsedRecords.filter(function (record) {
                return record.date >= start && record.date <= end;
            });
        }

        if (range === "weekly") {
            const start = getStartOfWeek(now);
            const end = new Date(start);

            end.setDate(start.getDate() + 7);

            return parsedRecords.filter(function (record) {
                return record.date >= start && record.date < end;
            });
        }

        if (range === "monthly") {
            return parsedRecords.filter(function (record) {
                return record.date.getFullYear() === now.getFullYear() &&
                    record.date.getMonth() === now.getMonth();
            });
        }

        if (range === "yearly") {
            return parsedRecords.filter(function (record) {
                return record.date.getFullYear() === now.getFullYear();
            });
        }

        if (range === "custom") {
            const start = getDateFromInput(startDateInput ? startDateInput.value : "", false);
            const end = getDateFromInput(endDateInput ? endDateInput.value : "", true);

            if (!start || !end) {
                return parsedRecords;
            }

            return parsedRecords.filter(function (record) {
                return record.date >= start && record.date <= end;
            });
        }

        return parsedRecords;
    }

    function getBmiCategory(bmi) {
        if (bmi < 18.5) {
            return "below-normal";
        }

        if (bmi < 25) {
            return "normal";
        }

        if (bmi < 30) {
            return "overweight";
        }

        return "obese";
    }

    function getPointColor(bmi) {
        const category = getBmiCategory(bmi);

        if (category === "below-normal") {
            return "#f59e0b";
        }

        if (category === "normal") {
            return "#0b9f6a";
        }

        if (category === "overweight") {
            return "#f97316";
        }

        return "#dc2626";
    }

    function getCategoryLabel(bmi) {
        const category = getBmiCategory(bmi);

        if (category === "below-normal") {
            return "Below Normal";
        }

        if (category === "normal") {
            return "Normal";
        }

        if (category === "overweight") {
            return "Overweight";
        }

        return "Obese";
    }

    function getXAxisLabel(record, range) {
        if (range === "daily") {
            return record.date.toLocaleTimeString("en-US", {
                hour: "numeric",
                minute: "2-digit"
            });
        }

        if (range === "yearly") {
            return record.date.toLocaleDateString("en-US", {
                month: "short"
            });
        }

        return formatShortDate(record.date);
    }

    function renderBmiTrendChart() {
        const range = chartRange.value;
        const filteredRecords = getFilteredRecords(range);

        const width = 720;
        const height = 320;
        const paddingLeft = 56;
        const paddingRight = 28;
        const paddingTop = 26;
        const paddingBottom = 58;

        const chartWidth = width - paddingLeft - paddingRight;
        const chartHeight = height - paddingTop - paddingBottom;

        const bmiValues = filteredRecords.map(function (record) {
            return record.bmi;
        });

        let minY = 15;
        let maxY = 35;

        if (bmiValues.length > 0) {
            minY = Math.max(0, Math.floor(Math.min(...bmiValues, 18.5) - 2));
            maxY = Math.ceil(Math.max(...bmiValues, 30) + 2);
        }

        function getX(index) {
            if (filteredRecords.length === 1) {
                return paddingLeft + chartWidth / 2;
            }

            return paddingLeft + (index / (filteredRecords.length - 1)) * chartWidth;
        }

        function getY(value) {
            return paddingTop + chartHeight - ((value - minY) / (maxY - minY)) * chartHeight;
        }

        let svgContent = "";

        const ySteps = 5;
        const stepValue = (maxY - minY) / ySteps;

        for (let index = 0; index <= ySteps; index++) {
            const value = Number((minY + stepValue * index).toFixed(1));
            const y = getY(value);

            svgContent += `
                <line
                    x1="${paddingLeft}"
                    y1="${y}"
                    x2="${width - paddingRight}"
                    y2="${y}"
                    class="bmi-grid-line" />

                <text
                    x="${paddingLeft - 14}"
                    y="${y + 4}"
                    class="bmi-axis-text"
                    text-anchor="end">${value}</text>
            `;
        }

        [18.5, 25, 30].forEach(function (value) {
            if (value < minY || value > maxY) {
                return;
            }

            const y = getY(value);

            svgContent += `
                <line
                    x1="${paddingLeft}"
                    y1="${y}"
                    x2="${width - paddingRight}"
                    y2="${y}"
                    class="bmi-reference-line" />

                <text
                    x="${width - paddingRight - 6}"
                    y="${y - 6}"
                    class="bmi-reference-text"
                    text-anchor="end">${value}</text>
            `;
        });

        svgContent += `
            <line
                x1="${paddingLeft}"
                y1="${paddingTop}"
                x2="${paddingLeft}"
                y2="${height - paddingBottom}"
                class="bmi-axis-line" />

            <line
                x1="${paddingLeft}"
                y1="${height - paddingBottom}"
                x2="${width - paddingRight}"
                y2="${height - paddingBottom}"
                class="bmi-axis-line" />
        `;

        filteredRecords.forEach(function (record, index) {
            const x = getX(index);

            const shouldShowLabel =
                filteredRecords.length <= 8 ||
                index === 0 ||
                index === filteredRecords.length - 1 ||
                index % Math.ceil(filteredRecords.length / 6) === 0;

            if (shouldShowLabel) {
                svgContent += `
                    <text
                        x="${x}"
                        y="${height - 24}"
                        class="bmi-axis-text"
                        text-anchor="middle">${getXAxisLabel(record, range)}</text>
                `;
            }
        });

        if (filteredRecords.length > 1) {
            for (let index = 1; index < filteredRecords.length; index++) {
                const previousRecord = filteredRecords[index - 1];
                const currentRecord = filteredRecords[index];

                const x1 = getX(index - 1);
                const y1 = getY(previousRecord.bmi);
                const x2 = getX(index);
                const y2 = getY(currentRecord.bmi);

                svgContent += `
                    <line
                        x1="${x1}"
                        y1="${y1}"
                        x2="${x2}"
                        y2="${y2}"
                        stroke="${getPointColor(currentRecord.bmi)}"
                        stroke-width="2.8"
                        stroke-linecap="round"
                        class="bmi-trend-segment" />
                `;
            }
        }

        filteredRecords.forEach(function (record, index) {
            const x = getX(index);
            const y = getY(record.bmi);
            const color = getPointColor(record.bmi);
            const categoryLabel = getCategoryLabel(record.bmi);

            svgContent += `
                <circle
                    cx="${x}"
                    cy="${y}"
                    r="4.8"
                    fill="${color}"
                    class="bmi-average-point">
                    <title>${record.patientName} - ${formatDateTime(record.date)}: BMI ${record.bmi} (${categoryLabel})</title>
                </circle>

                <text
                    x="${x}"
                    y="${y - 10}"
                    class="bmi-point-label"
                    text-anchor="middle">${record.bmi}</text>
            `;
        });

        if (filteredRecords.length === 0) {
            svgContent += `
                <text
                    x="${width / 2}"
                    y="${height / 2}"
                    class="bmi-empty-text"
                    text-anchor="middle">
                    No BMI records available for this period
                </text>
            `;
        }

        chartSvg.innerHTML = svgContent;

        const rangeText = chartRange.options[chartRange.selectedIndex].text;

        if (chartNote) {
            if (filteredRecords.length === 0) {
                chartNote.textContent = `${rangeText}: No BMI records available.`;
            } else if (filteredRecords.length === 1) {
                chartNote.textContent = `${rangeText}: 1 BMI record shown. Add more records to form a trend line.`;
            } else {
                chartNote.textContent = `${rangeText}: ${filteredRecords.length} BMI records shown with category-based color coding.`;
            }
        }
    }

    function toggleCustomRange() {
        if (!customRangeBox) {
            return;
        }

        if (chartRange.value === "custom") {
            customRangeBox.classList.remove("hidden");
        } else {
            customRangeBox.classList.add("hidden");
        }
    }

    chartRange.addEventListener("change", function () {
        toggleCustomRange();
        renderBmiTrendChart();
    });

    if (startDateInput) {
        startDateInput.addEventListener("change", renderBmiTrendChart);
    }

    if (endDateInput) {
        endDateInput.addEventListener("change", renderBmiTrendChart);
    }

    toggleCustomRange();
    renderBmiTrendChart();
});