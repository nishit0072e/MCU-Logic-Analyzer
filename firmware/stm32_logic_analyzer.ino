/*
 * STM32F103C6 DMA Logic Analyzer - UART Version
 * NOW WITH SLOW SAMPLE RATES (100Hz - 6MHz)
 * Hardware UART on PA9(TX)/PA10(RX)
 */

// Use hardware UART1 instead of USB Serial
HardwareSerial Serial1(PA10, PA9); // RX, TX
#define Serial Serial1
#define LED_BUILTIN PC13
#define BUFFER_SIZE 2048
#define BAUD_RATE 115200

// Sample buffer
uint16_t samples[BUFFER_SIZE];
volatile bool capturing = false;
volatile bool captureComplete = false;

// Sampling parameters
uint32_t sampleCount = BUFFER_SIZE;
uint32_t sampleRateHz = 100000; // Default: 100kHz (20ms window)

// HAL handles
TIM_HandleTypeDef htim2;
DMA_HandleTypeDef hdma_tim2_up;

// Timeout for stuck captures
uint32_t captureStartTime = 0;
#define CAPTURE_TIMEOUT_MS 30000 // 30 seconds (for slow rates)

void setup() {
  Serial.begin(BAUD_RATE);
  delay(100);

  // Configure GPIOB 0-7 as inputs
  pinMode(PA0, INPUT_PULLDOWN);
  pinMode(PA1, INPUT_PULLDOWN);
  pinMode(PA2, INPUT_PULLDOWN);
  pinMode(PA3, INPUT_PULLDOWN);
  pinMode(PA4, INPUT_PULLDOWN);
  pinMode(PA5, INPUT_PULLDOWN);
  pinMode(PA6, INPUT_PULLDOWN);
  pinMode(PA7, INPUT_PULLDOWN);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  initTimerDMA();

  Serial.println("READY:STM32-UART-LA8");
}

void loop() {
  // Check for capture timeout (important for slow rates)
  if (capturing && (millis() - captureStartTime > CAPTURE_TIMEOUT_MS)) {
    Serial.println("ERROR:TIMEOUT");
    stopCapture();
  }

  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == '\r' || cmd == '\n')
      return;
    handleCommand(cmd);
  }

  if (captureComplete) {
    captureComplete = false;
    sendCapture();
    digitalWrite(LED_BUILTIN, LOW);
  }

  // Blink when idle
  static uint32_t lastBlink = 0;
  if (!capturing && millis() - lastBlink > 500) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    lastBlink = millis();
  }
}

void handleCommand(char cmd) {
  switch (cmd) {
  case 'C':
  case 'c':
    startDMACapture();
    break;

  case 'I':
  case 'i':
    sendInfo();
    break;

  case 'R':
  case 'r':
    stopCapture();
    Serial.println("OK:RESET");
    break;

  // === SLOW RATES (for slow signals) ===
  case 'E':
    sampleRateHz = 100; // 100Hz = 20.48 second window
    Serial.println("OK:100Hz");
    break;

  case 'D':
    sampleRateHz = 1000; // 1kHz = 2.048 second window
    Serial.println("OK:1kHz");
    break;

  case 'B':
    sampleRateHz = 10000; // 10kHz = 204.8ms window
    Serial.println("OK:10kHz");
    break;

  case 'A':
    sampleRateHz = 100000; // 100kHz = 20.48ms window
    Serial.println("OK:100kHz");
    break;

  // === FAST RATES (for fast signals) ===
  case '1':
    sampleRateHz = 1000000; // 1MHz = 2.048ms window
    Serial.println("OK:1MHz");
    break;

  case '2':
    sampleRateHz = 2000000; // 2MHz = 1.024ms window
    Serial.println("OK:2MHz");
    break;

  case '5':
    sampleRateHz = 5000000; // 5MHz = 409.6µs window
    Serial.println("OK:5MHz");
    break;

  case '6':
    sampleRateHz = 6000000; // 6MHz = 341.3µs window
    Serial.println("OK:6MHz");
    break;

  default:
    Serial.println("ERROR:UNKNOWN_CMD");
  }
}

void initTimerDMA() {
  __HAL_RCC_TIM2_CLK_ENABLE();
  __HAL_RCC_DMA1_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 71;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;

  if (HAL_TIM_Base_Init(&htim2) != HAL_OK) {
    Serial.println("ERROR:TIM_INIT");
    return;
  }

  hdma_tim2_up.Instance = DMA1_Channel2;
  hdma_tim2_up.Init.Direction = DMA_PERIPH_TO_MEMORY;
  hdma_tim2_up.Init.PeriphInc = DMA_PINC_DISABLE;
  hdma_tim2_up.Init.MemInc = DMA_MINC_ENABLE;
  hdma_tim2_up.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
  hdma_tim2_up.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
  hdma_tim2_up.Init.Mode = DMA_NORMAL;
  hdma_tim2_up.Init.Priority = DMA_PRIORITY_HIGH;

  if (HAL_DMA_Init(&hdma_tim2_up) != HAL_OK) {
    Serial.println("ERROR:DMA_INIT");
    return;
  }

  // Register callbacks
  HAL_DMA_RegisterCallback(&hdma_tim2_up, HAL_DMA_XFER_CPLT_CB_ID,
                           DMA_XferCpltCallback);
  HAL_DMA_RegisterCallback(&hdma_tim2_up, HAL_DMA_XFER_ERROR_CB_ID,
                           DMA_XferErrorCallback);

  __HAL_LINKDMA(&htim2, hdma[TIM_DMA_ID_UPDATE], hdma_tim2_up);

  HAL_NVIC_SetPriority(DMA1_Channel2_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel2_IRQn);
}

void startDMACapture() {
  if (capturing) {
    Serial.println("ERROR:BUSY");
    return;
  }

  capturing = true;
  captureComplete = false;
  captureStartTime = millis();
  digitalWrite(LED_BUILTIN, HIGH);

  // Stop and reset timer/DMA
  HAL_TIM_Base_Stop(&htim2);
  __HAL_TIM_DISABLE_DMA(&htim2, TIM_DMA_UPDATE);
  HAL_DMA_Abort(&hdma_tim2_up);

  // Calculate timer period for desired sample rate
  // Timer freq = 72MHz / (prescaler+1) / (period+1)
  uint32_t period = (72000000 / sampleRateHz) - 1;

  // Clamp period to valid range
  if (period < 11)
    period = 11; // Max ~6MHz
  if (period > 65535)
    period = 65535; // Min ~1.1kHz with prescaler=0

  // For very slow rates, use prescaler
  uint32_t prescaler = 0;
  if (sampleRateHz < 1100) {
    // Use prescaler to achieve slower rates
    prescaler = (72000000 / (sampleRateHz * 65536)) + 1;
    period = (72000000 / (prescaler * sampleRateHz)) - 1;
  }

  __HAL_TIM_SET_PRESCALER(&htim2, prescaler);
  __HAL_TIM_SET_AUTORELOAD(&htim2, period);
  __HAL_TIM_SET_COUNTER(&htim2, 0);

  uint32_t gpio_idr = (uint32_t)&(GPIOA->IDR);

  HAL_StatusTypeDef status =
      HAL_DMA_Start_IT(&hdma_tim2_up, gpio_idr, (uint32_t)samples, sampleCount);

  if (status != HAL_OK) {
    Serial.print("ERROR:DMA_START:");
    Serial.println(status);
    capturing = false;
    digitalWrite(LED_BUILTIN, LOW);
    return;
  }

  __HAL_TIM_ENABLE_DMA(&htim2, TIM_DMA_UPDATE);
  HAL_TIM_Base_Start(&htim2);
}

void stopCapture() {
  HAL_TIM_Base_Stop(&htim2);
  __HAL_TIM_DISABLE_DMA(&htim2, TIM_DMA_UPDATE);
  HAL_DMA_Abort(&hdma_tim2_up);
  capturing = false;
  captureComplete = false;
  digitalWrite(LED_BUILTIN, LOW);
}

void DMA_XferCpltCallback(DMA_HandleTypeDef *hdma) {
  HAL_TIM_Base_Stop(&htim2);
  __HAL_TIM_DISABLE_DMA(&htim2, TIM_DMA_UPDATE);

  capturing = false;
  captureComplete = true;
}

void DMA_XferErrorCallback(DMA_HandleTypeDef *hdma) {
  Serial.println("ERROR:DMA_XFER");
  stopCapture();
}

extern "C" void DMA1_Channel2_IRQHandler(void) {
  HAL_DMA_IRQHandler(&hdma_tim2_up);
}

void sendCapture() {
  Serial.print("DATA:");

  Serial.write((uint8_t)(sampleCount & 0xFF));
  Serial.write((uint8_t)((sampleCount >> 8) & 0xFF));
  Serial.write((uint8_t)((sampleCount >> 16) & 0xFF));
  Serial.write((uint8_t)((sampleCount >> 24) & 0xFF));

  Serial.write((uint8_t)(sampleRateHz & 0xFF));
  Serial.write((uint8_t)((sampleRateHz >> 8) & 0xFF));
  Serial.write((uint8_t)((sampleRateHz >> 16) & 0xFF));
  Serial.write((uint8_t)((sampleRateHz >> 24) & 0xFF));

  Serial.write('\n');

  for (uint32_t i = 0; i < sampleCount; i++) {
    Serial.write((uint8_t)(samples[i] & 0xFF));
  }

  Serial.println("\nEND");
}

void sendInfo() {
  Serial.println("INFO:STM32-UART-LA8");
  Serial.println("VERSION:4.0-MULTIRATE");
  Serial.println("CHANNELS:8");
  Serial.print("BUFFER:");
  Serial.println(BUFFER_SIZE);
  Serial.print("RATE:");
  Serial.print(sampleRateHz);
  Serial.println("Hz");
  Serial.println("RATES:100Hz,1kHz,10kHz,100kHz,1MHz,2MHz,5MHz,6MHz");
  Serial.print("STATUS:");
  Serial.println(capturing ? "BUSY" : "READY");
}
