<template>
  <div class="h-full flex flex-col relative z-10 w-full max-w-[1400px] mx-auto pt-4">
    <!-- 搜索区 -->
    <div class="bg-card rounded-xl border border-border/40 p-3 shadow-sm mb-3 shrink-0">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="flex items-center gap-2">
          <span class="text-xs font-medium text-muted-foreground shrink-0 w-16">产出码</span>
          <input v-model="outputCode" type="text" placeholder="输入产出码追溯"
            class="flex-1 px-3 py-1.5 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all"
            @keyup.enter="handleOutputSearch" />
          <button class="px-3 py-1.5 bg-accent text-white rounded-lg text-xs font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 shrink-0" :disabled="outputLoading || !outputCode.trim()" @click="handleOutputSearch">
            <svg v-if="outputLoading" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </button>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-medium text-muted-foreground shrink-0 w-16">投入码</span>
          <input v-model="inputCode" type="text" placeholder="输入投入码查询关联产出"
            class="flex-1 px-3 py-1.5 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all"
            @keyup.enter="handleInputSearch" />
          <button class="px-3 py-1.5 bg-accent text-white rounded-lg text-xs font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 shrink-0" :disabled="inputLoading || !inputCode.trim()" @click="handleInputSearch">
            <svg v-if="inputLoading" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-show="searched" class="bg-card rounded-xl border border-border/40 shadow-sm flex flex-col flex-1 min-h-0">
      <div class="px-4 py-2 border-b border-border/40 bg-muted/20 flex items-center justify-between shrink-0">
        <span class="text-sm text-muted-foreground">
          <template v-if="traceSteps.length > 0">
            追溯链路共 <strong class="text-foreground">{{ traceSteps.length }}</strong> 步
          </template>
          <template v-else>
            未找到追溯链路
          </template>
          <span v-if="searchedCode" class="ml-2 text-xs">— 追溯码: <code class="bg-muted px-1.5 py-0.5 rounded text-accent">{{ searchedCode }}</code></span>
        </span>
      </div>

      <div v-if="traceSteps.length === 0 && !searchError" class="py-8 text-center text-muted-foreground shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>未找到该产出码的追溯记录</p>
      </div>

      <div v-if="searchError" class="py-8 text-center shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-red-500 font-medium">{{ searchError }}</p>
      </div>

      <div v-else class="overflow-auto flex-1 min-h-0">
        <table class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-muted/50 z-10">
            <tr class="border-b border-border text-xs uppercase tracking-wider text-muted-foreground">
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-12 text-center">#</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">工序编码</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">工序名称</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">物料编码</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">物料类型</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">条码</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">操作时间</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">设备名称</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">检测结果</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">操作人</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-64 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/50 text-sm">
            <tr v-for="(step, idx) in traceSteps" :key="step.workorder_code + '-' + idx"
              class="hover:bg-accent/5 transition-colors"
              :class="{'bg-muted/10': step.level > 0}">
              <td class="px-3 py-2.5 text-center">
                <span class="inline-flex items-center justify-center w-6 h-6 rounded text-xs font-bold" :class="stepBadgeClass(step)">{{ idx + 1 }}</span>
              </td>
              <td class="px-3 py-2.5 font-mono text-xs">{{ step.procedure_code }}</td>
              <td class="px-3 py-2.5 text-sm">{{ step.procedure_name || '-' }}</td>
              <td class="px-3 py-2.5 font-mono text-xs">{{ step.material_code }}</td>
              <td class="px-3 py-2.5"><material-type-tag :type="step.material_type" /></td>
              <td class="px-3 py-2.5 font-mono text-xs max-w-[180px] truncate" :title="step.qr_code">{{ step.qr_code }}</td>
              <td class="px-3 py-2.5 text-muted-foreground text-xs">{{ fmtTime(step.op_time) }}</td>
              <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ step.device_name || step.device_code || '-' }}</td>
              <td class="px-3 py-2.5"><span :class="checkResultClass(step.check_result)">{{ step.check_result || '-' }}</span></td>
              <td class="px-3 py-2.5 text-sm">{{ step.operator }}</td>
              <td class="px-3 py-2.5 text-center">
                <div class="grid grid-cols-2 gap-1.5">
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors" @click="openInputModal(step)">查看投入</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors" @click="openProcessParamModal(step)">工艺参数</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200 transition-colors" @click="openInspectionModal(step)">检验单</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-purple-50 text-purple-600 hover:bg-purple-100 border border-purple-200 transition-colors" @click="openSubmissionModal(step)">提交记录</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 投入物料弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
      <div v-if="inputModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeInputModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">投入物料明细</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ modalStep?.procedure_name || '工序' }}
                <span v-if="modalStep?.procedure_code" class="ml-1 font-mono">({{ modalStep?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ modalStep?.qr_code }}</code></span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeInputModal">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="modalLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="modalError" class="text-sm text-red-500 py-4 text-center">{{ modalError }}</div>
            <div v-else-if="modalInputs.length === 0" class="text-sm text-muted-foreground py-8 text-center">该次报工无投入记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-[120px]">物料编码</th>
                    <th class="px-3 py-2.5 font-medium w-20">物料类型</th>
                    <th class="px-3 py-2.5 font-medium">条码</th>
                    <th class="px-3 py-2.5 font-medium w-12 text-center">数量</th>
                    <th class="px-3 py-2.5 font-medium w-36">操作时间</th>
                    <th class="px-3 py-2.5 font-medium w-24 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(input, i) in modalInputs" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 font-mono text-xs">{{ input.material_code }}</td>
                    <td class="px-3 py-2.5"><material-type-tag :type="input.material_type" /></td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[200px] truncate" :title="input.qr_code">{{ input.qr_code }}</td>
                    <td class="px-3 py-2.5 text-center">{{ input.require_num }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(input.op_time) }}</td>
                    <td class="px-3 py-2.5 text-center">
                      <button class="px-2 py-1 rounded text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors"
                        @click="traceInputCode(input.qr_code)">追溯此码</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </transition>
    </Teleport>

    <!-- 工艺参数弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
      <div v-if="paramModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeParamModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">工艺参数</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ paramStep?.procedure_name || '工序' }}
                <span v-if="paramStep?.procedure_code" class="ml-1 font-mono">({{ paramStep?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ paramStep?.qr_code }}</code></span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button class="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent text-white hover:bg-accent/90 transition-colors flex items-center gap-1.5" @click="goDeviceDataFromParam">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"/></svg>
                数采数据
              </button>
              <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeParamModal">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="paramLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="paramError" class="text-sm text-red-500 py-4 text-center">{{ paramError }}</div>
            <div v-else-if="paramData.length === 0" class="text-sm text-muted-foreground py-8 text-center">该工单无工艺参数数据</div>
            <div v-else class="space-y-4">
              <div v-for="(item, idx) in paramData" :key="idx" class="rounded-lg border border-border/50 bg-muted/10 p-4">
                <div class="flex items-center justify-between mb-2 text-xs text-muted-foreground">
                  <span class="font-medium">{{ item.device_name || item.device_code }} — {{ item.procedure_name }}</span>
                  <span>{{ fmtTime(item.timestamp) }}</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  <div v-for="(val, key) in item.params" :key="key" class="bg-white rounded border border-border/40 px-3 py-2">
                    <p class="text-[10px] text-muted-foreground font-mono">{{ item.param_descs?.[key] || key }}</p>
                    <p class="text-sm font-semibold text-foreground">{{ val }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
    </Teleport>

    <!-- 提交记录弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
      <div v-if="subModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeSubModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">提交记录</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ subStep?.procedure_name || '工序' }}
                <span v-if="subStep?.procedure_code" class="ml-1 font-mono">({{ subStep?.procedure_code }})</span>
                <span class="ml-2">条码: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ subStep?.qr_code }}</code></span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeSubModal">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="subLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="subError" class="text-sm text-red-500 py-4 text-center">{{ subError }}</div>
            <div v-else-if="subRecords.length === 0" class="text-sm text-muted-foreground py-8 text-center">无提交记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-14 text-center">#</th>
                    <th class="px-3 py-2.5 font-medium">工单编码</th>
                    <th class="px-3 py-2.5 font-medium w-36">操作时间</th>
                    <th class="px-3 py-2.5 font-medium">操作人</th>
                    <th class="px-3 py-2.5 font-medium">检测结果</th>
                    <th class="px-3 py-2.5 font-medium w-44 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(rec, i) in subRecords" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 text-center text-muted-foreground">{{ i + 1 }}</td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[250px] truncate" :title="rec.workorder_code">{{ rec.workorder_code }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(rec.op_time) }}</td>
                    <td class="px-3 py-2.5">{{ rec.operator }}</td>
                    <td class="px-3 py-2.5"><span class="text-xs" :class="checkResultClass(rec.check_result)">{{ rec.check_result || '-' }}</span></td>
                    <td class="px-3 py-2.5 text-center">
                      <div class="grid grid-cols-2 gap-1.5">
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors" @click="openInputFromSub(rec)">查看投入</button>
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors" @click="openProcessParamFromSub(rec)">工艺参数</button>
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200 transition-colors" @click="openInspectionFromSub(rec)">检验单</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </transition>
    </Teleport>

    <!-- 检验单弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
      <div v-if="inspectionModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeInspectionModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">检验单</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ inspectionStep?.procedure_name || '工序' }}
                <span v-if="inspectionStep?.procedure_code" class="ml-1 font-mono">({{ inspectionStep?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ inspectionStep?.qr_code }}</code></span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="inspectionData && inspectionData.is_qualified != null"
                class="text-xs font-bold px-3 py-1 rounded-full"
                :class="inspectionData.is_qualified ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600'">
                {{ inspectionData.is_qualified ? '整体合格' : '存在不合格项' }}
              </span>
              <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeInspectionModal">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="inspectionLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="inspectionError" class="text-sm text-red-500 py-4 text-center">{{ inspectionError }}</div>
            <div v-else-if="!inspectionData" class="text-sm text-muted-foreground py-8 text-center">该报工无检验单记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-14 text-center">#</th>
                    <th class="px-3 py-2.5 font-medium">检验项名称</th>
                    <th class="px-3 py-2.5 font-medium w-28">类型</th>
                    <th class="px-3 py-2.5 font-medium w-36">数据范围</th>
                    <th class="px-3 py-2.5 font-medium">检验要求</th>
                    <th class="px-3 py-2.5 font-medium w-36">检验工具</th>
                    <th class="px-3 py-2.5 font-medium">填写值</th>
                    <th class="px-3 py-2.5 font-medium w-24 text-center">结果</th>
                    <th class="px-3 py-2.5 font-medium w-28">不合格原因</th>
                    <th class="px-3 py-2.5 font-medium w-28 text-center">图片</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(item, i) in inspectionItems" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 text-center text-muted-foreground">{{ i + 1 }}</td>
                    <td class="px-3 py-2.5">
                      <span class="font-medium">{{ item.item_name }}</span>
                      <span class="ml-1 font-mono text-[10px] text-muted-foreground">{{ item.item_code }}</span>
                    </td>
                    <td class="px-3 py-2.5">
                      <span class="text-xs" :class="item.inspect_type === 'range' ? 'text-amber-600' : 'text-blue-600'">{{ item.inspect_type === 'range' ? '数据范围' : '是否合格' }}</span>
                    </td>
                    <td class="px-3 py-2.5 font-mono text-xs">{{ item.range_value || '-' }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground whitespace-normal break-words">{{ item.requirement || '-' }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground whitespace-normal break-words">{{ item.tool || '-' }}</td>
                    <td class="px-3 py-2.5 font-mono text-xs">{{ item.input_value ?? '-' }}</td>
                    <td class="px-3 py-2.5 text-center">
                      <span class="text-xs font-medium" :class="item.is_qualified ? 'text-teal-600' : 'text-red-600'">{{ item.is_qualified ? '合格' : '不合格' }}</span>
                    </td>
                    <td class="px-3 py-2.5">
                      <button v-if="unqualifiedReasonCount(item) > 0"
                        class="px-2.5 py-1 rounded-md text-xs font-medium bg-red-50 text-red-600 hover:bg-red-100 border border-red-200 transition-colors"
                        @click="showUnqualifiedReasons(item)">查看原因 ({{ unqualifiedReasonCount(item) }})</button>
                      <span v-else class="text-xs text-muted-foreground">-</span>
                    </td>
                    <td class="px-3 py-2.5 text-center">
                      <button v-if="imageCount(item) > 0"
                        class="px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border border-indigo-200 transition-colors"
                        @click="showImages(item)">查看图片 ({{ imageCount(item) }})</button>
                      <span v-else class="text-xs text-muted-foreground">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="flex items-center justify-between mt-4 text-xs text-muted-foreground px-1">
                <span>操作人: {{ inspectionData.operator || '-' }}</span>
                <span>检验时间: {{ fmtTime(inspectionData.op_time) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
    </Teleport>

    <!-- 不合格原因明细弹窗（检验单弹窗内逐项点击查看） -->
    <Teleport to="body">
      <transition name="modal-fade">
      <div v-if="reasonDetailVisible" class="fixed inset-0 z-[1100] flex items-center justify-center bg-black/30" @click.self="closeUnqualifiedReasons">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[70vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-5 py-3.5 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">不合格原因</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                检验项: {{ reasonDetailItem?.item_name || '-' }}
                <span v-if="reasonDetailItem?.item_code" class="ml-1 font-mono">({{ reasonDetailItem.item_code }})</span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeUnqualifiedReasons">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto p-5">
            <div v-if="reasonDetailItem && unqualifiedReasonCount(reasonDetailItem) > 0" class="space-y-2">
              <div v-for="(r, ri) in reasonDetailItem.unqualified_reasons" :key="ri" class="flex items-center justify-between gap-3 rounded-lg border border-border/50 bg-muted/20 px-3 py-2">
                <span class="text-sm text-foreground">{{ r?.reason_name || r?.reason_code || '-' }}</span>
                <span v-if="r?.reason_code" class="font-mono text-[10px] text-muted-foreground">{{ r.reason_code }}</span>
              </div>
            </div>
            <p v-else class="text-sm text-muted-foreground text-center py-4">该检验项无不合格原因</p>
          </div>
        </div>
      </div>
    </transition>
    </Teleport>

    <!-- 检验单内基准/实际图片查看弹窗：图片存 manual_line 服务器磁盘、DB 只存路径，
         经 manual_line 的 download_image 接口（跨服务、与 mgDMS 下载同约定不加登录鉴权）按路径回显 -->
    <Teleport to="body">
      <transition name="modal-fade">
      <div v-if="imageDetailVisible" class="fixed inset-0 z-[1100] flex items-center justify-center bg-black/30" @click.self="closeImages">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-5 py-3.5 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">检验项图片</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                检验项: {{ imageDetailItem?.item_name || '-' }}
                <span v-if="imageDetailItem?.item_code" class="ml-1 font-mono">({{ imageDetailItem.item_code }})</span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeImages">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto p-5">
            <div v-if="imageDetailLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-10">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              图片加载中...
            </div>
            <div v-else>
              <div v-if="imageDetailError" class="text-xs text-red-500 mb-3">{{ imageDetailError }}</div>
              <div v-if="imageDetailItem?.baseline_image" class="mb-5">
                <p class="text-xs font-bold text-muted-foreground mb-2">基准图片（档案配置）</p>
                <!-- 滚轮/双指以光标为锚点缩放，放大后按住可自由拖动 -->
                <div v-if="imageDetailBaselineUrl" class="w-full h-[45vh] rounded-lg border border-border/60 bg-muted/10 overflow-hidden">
                  <PanZoomImage :src="imageDetailBaselineUrl" alt="基准图片" compact />
                </div>
                <p v-else class="text-xs text-muted-foreground">基准图片加载失败或已不存在</p>
              </div>
              <div v-if="imageDetailItem?.actual_image">
                <p class="text-xs font-bold text-muted-foreground mb-2">实际图片（报工上传）</p>
                <!-- 滚轮/双指以光标为锚点缩放，放大后按住可自由拖动 -->
                <div v-if="imageDetailActualUrl" class="w-full h-[45vh] rounded-lg border border-border/60 bg-muted/10 overflow-hidden">
                  <PanZoomImage :src="imageDetailActualUrl" alt="实际图片" compact />
                </div>
                <p v-else class="text-xs text-muted-foreground">实际图片加载失败或已不存在</p>
              </div>
              <p v-if="!imageDetailItem?.baseline_image && !imageDetailItem?.actual_image" class="text-sm text-muted-foreground text-center py-4">该检验项未上传图片</p>
            </div>
          </div>
        </div>
      </div>
    </transition>
    </Teleport>

    <!-- 投入码选产出的弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
      <div v-if="inputCodeModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeInputCodeModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">选择产出码</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                投入码 <code class="bg-muted px-1 py-0.5 rounded font-mono">{{ inputCode }}</code> 关联了以下产出码，请选择一条进行追溯
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeInputCodeModal">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="inputCodeLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              查询中...
            </div>
            <div v-else-if="inputCodeError" class="text-sm text-red-500 py-4 text-center">{{ inputCodeError }}</div>
            <div v-else-if="inputCodeOptions.length === 0" class="text-sm text-muted-foreground py-8 text-center">未找到关联的产出码</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-14 text-center">#</th>
                    <th class="px-3 py-2.5 font-medium">工序名称</th>
                    <th class="px-3 py-2.5 font-medium">物料编码</th>
                    <th class="px-3 py-2.5 font-medium">物料类型</th>
                    <th class="px-3 py-2.5 font-medium">产出码</th>
                    <th class="px-3 py-2.5 font-medium">操作时间</th>
                    <th class="px-3 py-2.5 font-medium w-24 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(opt, i) in inputCodeOptions" :key="opt.qr_code" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 text-center text-muted-foreground">{{ i + 1 }}</td>
                    <td class="px-3 py-2.5">{{ opt.procedure_name || '-' }}</td>
                    <td class="px-3 py-2.5 font-mono text-xs">{{ opt.material_code }}</td>
                    <td class="px-3 py-2.5"><material-type-tag :type="opt.material_type" /></td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[200px] truncate" :title="opt.qr_code">{{ opt.qr_code }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(opt.op_time) }}</td>
                    <td class="px-3 py-2.5 text-center">
                      <button class="px-3 py-1.5 rounded-md text-xs font-medium bg-accent text-white hover:bg-accent/90 transition-colors" @click="selectInputCodeOutput(opt)">选择</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, inject, computed, defineComponent, h, onBeforeUnmount } from 'vue'
import type { Ref } from 'vue'
import api from '../api/trace-app'
import { _postBlob } from '../api/httpWrap'
import { showToast } from '../utils/dialog'
import { navigateToDeviceData } from '../composables/useDeviceDataNav'
import PanZoomImage from '../components/ui/PanZoomImage.vue'

const currentView = inject<Ref<string>>('currentView', ref('home'))

const outputCode = ref('')
const inputCode = ref('')
const searchedCode = ref('')
const outputLoading = ref(false)
const inputLoading = ref(false)
const searched = ref(false)
const searchError = ref('')
const traceSteps = ref<any[]>([])

// 投入物料弹窗
const inputModalVisible = ref(false)
const modalStep = ref<any>(null)
const modalInputs = ref<any[]>([])
const modalLoading = ref(false)
const modalError = ref('')

// 工艺参数弹窗
const paramModalVisible = ref(false)
const paramStep = ref<any>(null)
const paramData = ref<any[]>([])
const paramLoading = ref(false)
const paramError = ref('')

// 检验单弹窗
const inspectionModalVisible = ref(false)
const inspectionStep = ref<any>(null)
const inspectionData = ref<any>(null)
const inspectionLoading = ref(false)
const inspectionError = ref('')
const inspectionItems = computed<any[]>(() => inspectionData.value?.items || [])

// 检验单弹窗内「不合格原因」明细弹窗（行内按钮点击查看）
const reasonDetailVisible = ref(false)
const reasonDetailItem = ref<any>(null)
const showUnqualifiedReasons = (item: any) => {
  reasonDetailItem.value = item
  reasonDetailVisible.value = true
}
const closeUnqualifiedReasons = () => {
  reasonDetailVisible.value = false
  reasonDetailItem.value = null
}

// ========== 检验单基准/实际图片查看 ==========
// 图片由 manual_line_general_traceability 报工/配置时上传存服务器磁盘，inspection_records 快照只存文件路径。
// 经 manual_line 的 download_image 接口按路径回显（同 mgDMS 下载文件约定：不加登录鉴权，
// 该接口只接受纯文件名路径、无路径穿越），trace_app 以同源应用前缀路径跨服务取图。
const MANUAL_IMAGE_DOWNLOAD_URL = '/api/manual_line_general_traceability/inspection_item/download_image'

const readBlobText = (blob: Blob) => new Promise<string>((resolve, reject) => {
  const reader = new FileReader()
  reader.onerror = () => reject(new Error('读取响应失败'))
  reader.onload = () => resolve(String(reader.result || ''))
  reader.readAsText(blob)
})

// 按 manual_line 落库的图片路径读回图片，返回 objectURL（调用方负责 revoke）。
// httpWrap 响应拦截器已把 axios 响应解包为 response.data——responseType='blob' 时返回值即 Blob 本身。
const loadManualImageUrl = async (path: string): Promise<string> => {
  const blob: any = await _postBlob(MANUAL_IMAGE_DOWNLOAD_URL, { path })
  if (!blob || !(blob instanceof Blob)) {
    throw new Error('图片回显失败')
  }
  // 后端文件缺失/参数不合法时返回 JSON（blob.type 为 application/json），转成可读错误
  if (blob.type && blob.type.indexOf('json') >= 0) {
    let info = '图片不存在'
    try {
      info = JSON.parse(await readBlobText(blob)).info || info
    } catch (e) {
      // 解析失败保持默认提示
    }
    throw new Error(info)
  }
  return URL.createObjectURL(blob)
}

const imageDetailVisible = ref(false)
const imageDetailItem = ref<any>(null)
const imageDetailLoading = ref(false)
const imageDetailError = ref('')
const imageDetailBaselineUrl = ref('')
const imageDetailActualUrl = ref('')

// 某检验项可看的图片张数（基准 + 实际，存了路径才算）
const imageCount = (item: any) => {
  let count = 0
  if (item?.baseline_image) count += 1
  if (item?.actual_image) count += 1
  return count
}

const revokeImageDetailUrls = () => {
  if (imageDetailBaselineUrl.value) {
    URL.revokeObjectURL(imageDetailBaselineUrl.value)
    imageDetailBaselineUrl.value = ''
  }
  if (imageDetailActualUrl.value) {
    URL.revokeObjectURL(imageDetailActualUrl.value)
    imageDetailActualUrl.value = ''
  }
}

const showImages = async (item: any) => {
  imageDetailItem.value = item
  imageDetailError.value = ''
  imageDetailVisible.value = true
  revokeImageDetailUrls()
  const baseline = item?.baseline_image || ''
  const actual = item?.actual_image || ''
  imageDetailLoading.value = true
  // 基准/实际图独立加载：任一张失败不影响另一张展示，错误统一提示
  const errors: string[] = []
  try {
    if (baseline) {
      try {
        imageDetailBaselineUrl.value = await loadManualImageUrl(baseline)
      } catch (err: any) {
        errors.push('基准图片: ' + (err?.message || '加载失败'))
      }
    }
    if (actual) {
      try {
        imageDetailActualUrl.value = await loadManualImageUrl(actual)
      } catch (err: any) {
        errors.push('实际图片: ' + (err?.message || '加载失败'))
      }
    }
  } catch (err: any) {
    errors.push(err?.message || '图片加载失败')
  } finally {
    imageDetailLoading.value = false
    imageDetailError.value = errors.length > 0 ? errors.join('；') : ''
  }
}

const closeImages = () => {
  imageDetailVisible.value = false
  revokeImageDetailUrls()
  imageDetailItem.value = null
}

// 弹窗关闭后仍残留的 objectURL（极端场景下组件卸载）释放，防泄漏
onBeforeUnmount(() => {
  revokeImageDetailUrls()
})

// 提交记录弹窗
const subModalVisible = ref(false)
const subStep = ref<any>(null)
const subRecords = ref<any[]>([])
const subLoading = ref(false)
const subError = ref('')

// 投入码选择弹窗
const inputCodeModalVisible = ref(false)
const inputCodeLoading = ref(false)
const inputCodeError = ref('')
const inputCodeOptions = ref<any[]>([])

// ========== 产出码追溯 ==========
const handleOutputSearch = async () => {
  const code = outputCode.value.trim()
  if (!code) return
  traceSteps.value = []
  searched.value = false
  searchError.value = ''
  outputLoading.value = true
  searchedCode.value = code
  try {
    const res = await api.queryByOutput(code)
    traceSteps.value = res.data || []
    searched.value = true
    searchError.value = ''
  } catch (err: any) {
    console.error('查询失败:', err)
    traceSteps.value = []
    searchError.value = '查询失败，请检查网络或稍后重试'
  } finally {
    outputLoading.value = false
  }
}

// ========== 投入码追溯 ==========
const handleInputSearch = async () => {
  const code = inputCode.value.trim()
  if (!code) return
  await queryInputCodeOutputs(code)
}

// ========== 投入码查询 ==========
const queryInputCodeOutputs = async (code: string) => {
  inputCodeModalVisible.value = true
  inputCodeLoading.value = true
  inputCodeError.value = ''
  inputCodeOptions.value = []
  try {
    const res = await api.queryOutputsByInput(code)
    inputCodeOptions.value = res.data || []
  } catch (err: any) {
    inputCodeError.value = '查询失败: ' + (err?.message || '未知错误')
  } finally {
    inputCodeLoading.value = false
  }
}

const closeInputCodeModal = () => {
  inputCodeModalVisible.value = false
}

const selectInputCodeOutput = (opt: any) => {
  inputCodeModalVisible.value = false
  outputCode.value = opt.qr_code
  searchedCode.value = opt.qr_code
  handleOutputSearch()
}

// ========== 投入弹窗 ==========
const openInputModal = async (step: any) => {
  modalStep.value = step
  inputModalVisible.value = true
  modalLoading.value = true
  modalError.value = ''
  modalInputs.value = []
  try {
    const res = await api.queryInputs(step.workorder_code)
    modalInputs.value = res.data || []
  } catch (err: any) {
    modalError.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    modalLoading.value = false
  }
}

const closeInputModal = () => {
  inputModalVisible.value = false
  modalStep.value = null
  modalInputs.value = []
}

const traceInputCode = (qrCode: string) => {
  closeInputModal()
  inputCode.value = qrCode
  handleInputSearch()
}

// ========== 工艺参数弹窗 ==========
const openProcessParamModal = async (step: any) => {
  paramStep.value = step
  paramModalVisible.value = true
  paramLoading.value = true
  paramError.value = ''
  paramData.value = []
  try {
    const res = await api.queryProcessParams(step.workorder_code)
    paramData.value = res.data || []
  } catch (err: any) {
    paramError.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    paramLoading.value = false
  }
}

const closeParamModal = () => {
  paramModalVisible.value = false
  paramStep.value = null
  paramData.value = []
}

// ========== 数采数据：跳转数采查询并携带设备 + 报工时间±5min ==========
const goDeviceDataFromParam = () => {
  const step = paramStep.value
  const ok = navigateToDeviceData({
    device_code: step?.device_code || '',
    report_time: step?.op_time || '',
  })
  if (!ok) {
    showToast('该报工记录缺少设备或报工时间，无法跳转数采查询', 'warning')
    return
  }
  closeParamModal()
  currentView.value = 'device_data'
}

// ========== 提交记录弹窗 ==========
const openSubmissionModal = async (step: any) => {
  subStep.value = step
  subModalVisible.value = true
  subLoading.value = true
  subError.value = ''
  subRecords.value = []
  try {
    const res = await api.querySubmissionRecords(step.qr_code, step.procedure_code, step.device_code)
    subRecords.value = res.data || []
  } catch (err: any) {
    subError.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    subLoading.value = false
  }
}

const closeSubModal = () => {
  subModalVisible.value = false
  subStep.value = null
  subRecords.value = []
}

// 从提交记录弹窗打开投入弹窗：先关提交记录，再开投入，避免 z-index 遮挡
const openInputFromSub = (rec: any) => {
  const step = {
    workorder_code: rec.workorder_code,
    procedure_name: subStep.value?.procedure_name,
    procedure_code: subStep.value?.procedure_code,
    qr_code: subStep.value?.qr_code,
  }
  closeSubModal()
  openInputModal(step)
}

// 从提交记录弹窗打开工艺参数弹窗：先关提交记录，再开工艺参数，避免 z-index 遮挡
// 补带 device_code / op_time，供「数采数据」按钮跳转使用（rec 为提交记录本身，op_time 更精确）
const openProcessParamFromSub = (rec: any) => {
  const step = {
    workorder_code: rec.workorder_code,
    procedure_name: subStep.value?.procedure_name,
    procedure_code: subStep.value?.procedure_code,
    qr_code: subStep.value?.qr_code,
    device_code: subStep.value?.device_code || rec.device_code,
    op_time: rec.op_time || subStep.value?.op_time,
  }
  closeSubModal()
  openProcessParamModal(step)
}

// ========== 检验单弹窗 ==========
const openInspectionModal = async (step: any) => {
  inspectionStep.value = step
  inspectionModalVisible.value = true
  inspectionLoading.value = true
  inspectionError.value = ''
  inspectionData.value = null
  try {
    const res = await api.queryInspectionRecord(step.workorder_code)
    inspectionData.value = res.data || null
  } catch (err: any) {
    inspectionError.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    inspectionLoading.value = false
  }
}

const closeInspectionModal = () => {
  inspectionModalVisible.value = false
  inspectionStep.value = null
  inspectionData.value = null
}

// 从提交记录弹窗打开检验单弹窗：先关提交记录，再开检验单，避免 z-index 遮挡
const openInspectionFromSub = (rec: any) => {
  const step = {
    workorder_code: rec.workorder_code,
    procedure_name: subStep.value?.procedure_name,
    procedure_code: subStep.value?.procedure_code,
    qr_code: subStep.value?.qr_code,
  }
  closeSubModal()
  openInspectionModal(step)
}

// ========== 工具 ==========
const fmtTime = (t: string) => t ? t.replace(/\.\d+$/, '') : '-'

// 某检验项选中的不合格原因条数（非数组/缺键按 0 计，0 = 无原因可看）
const unqualifiedReasonCount = (item: any) =>
  Array.isArray(item?.unqualified_reasons) ? item.unqualified_reasons.length : 0

const checkResultClass = (v: string) => {
  if (!v || v === '-') return ''
  if (v === '一次合格' || v === 'OK') return 'text-teal-600 font-medium'
  if (v === '返工合格') return 'text-amber-600 font-medium'
  if (v === '复投合格') return 'text-blue-600 font-medium'
  return 'text-red-600 font-medium'
}

const stepBadgeClass = (step: any) => {
  const t = step.material_type
  if (t === 'finished_product') return 'bg-teal-100 text-teal-700'
  if (t === 'semi_finished_product') return 'bg-blue-100 text-blue-700'
  if (t === 'raw_material') return 'bg-amber-100 text-amber-700'
  return 'bg-muted text-muted-foreground'
}

// 物料类型标签组件
const MaterialTypeTag = defineComponent({
  name: 'MaterialTypeTag',
  props: { type: String },
  setup(props: any) {
    const labels: Record<string, string> = {
      raw_material: '原材料',
      semi_finished_product: '半成品',
      finished_product: '成品',
    }
    const colors: Record<string, string> = {
      raw_material: 'bg-amber-50 text-amber-600 border-amber-200',
      semi_finished_product: 'bg-blue-50 text-blue-600 border-blue-200',
      finished_product: 'bg-teal-50 text-teal-600 border-teal-200',
    }
    return () => {
      const type = props.type || ''
      const label = labels[type] || type
      const color = colors[type] || 'bg-gray-50 text-gray-600 border-gray-200'
      return h('span', {
        class: `inline-block px-2 py-0.5 rounded text-xs font-medium border ${color}`
      }, label)
    }
  }
})
</script>

<style scoped>
.modal-fade-enter-active {
  transition: opacity 0.15s ease-out;
}
.modal-fade-leave-active {
  transition: opacity 0.1s ease-in;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
